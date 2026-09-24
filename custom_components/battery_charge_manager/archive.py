"""Transactional, lossless raw archive. No automatic deletion or compaction.

Every method does blocking I/O and must run in an executor from Home Assistant.
Only derived checkpoints/indexes are replaceable. Raw observations, samples and
original/analysis documents are protected against UPDATE and DELETE by SQLite.
"""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable, Iterator

ARCHIVE_VERSION = 1


def encoded(value: Any) -> str:
    """Canonical lossless JSON for hashes; never round measurement values."""
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                      separators=(',', ':'))


def digest(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


class RawArchive:
    """Per-config-entry SQLite archive with independent short transactions."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    @contextmanager
    def _connection(self, *, write: bool = False):
        connection = sqlite3.connect(self.path, timeout=30, isolation_level=None,
                                     check_same_thread=False)
        try:
            connection.execute('PRAGMA foreign_keys=ON')
            connection.execute('PRAGMA synchronous=FULL')
            connection.execute('BEGIN IMMEDIATE' if write else 'BEGIN')
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self, legacy: dict[str, Any] | None = None) -> dict[str, Any]:
        """Import once atomically; leave the original HA Store untouched."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=30)
        try:
            version = connection.execute('PRAGMA user_version').fetchone()[0]
            if version not in (0, ARCHIVE_VERSION):
                raise ValueError(f'Unsupported raw archive version: {version}')
            connection.execute('PRAGMA journal_mode=WAL')
            connection.executescript('''
                CREATE TABLE IF NOT EXISTS traces (
                    id TEXT PRIMARY KEY, sample_count INTEGER NOT NULL DEFAULT 0,
                    chain_hash TEXT NOT NULL DEFAULT '', event_count INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS samples (
                    trace_id TEXT NOT NULL REFERENCES traces(id), seq INTEGER NOT NULL,
                    timestamp TEXT, payload TEXT NOT NULL, chain_hash TEXT NOT NULL,
                    PRIMARY KEY(trace_id,seq)
                );
                CREATE INDEX IF NOT EXISTS sample_time ON samples(trace_id,timestamp,seq);
                CREATE TABLE IF NOT EXISTS events (
                    trace_id TEXT NOT NULL REFERENCES traces(id), seq INTEGER NOT NULL,
                    payload TEXT NOT NULL, PRIMARY KEY(trace_id,seq)
                );
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY, kind TEXT NOT NULL, hash TEXT NOT NULL,
                    payload TEXT NOT NULL, UNIQUE(kind,hash)
                );
                CREATE TABLE IF NOT EXISTS checkpoints (key TEXT PRIMARY KEY, payload TEXT NOT NULL);
            ''')
            for table in ('samples', 'events', 'documents'):
                for action in ('UPDATE', 'DELETE'):
                    connection.execute(
                        f'CREATE TRIGGER IF NOT EXISTS protect_{table}_{action.lower()} '
                        f'BEFORE {action} ON {table} BEGIN '
                        "SELECT RAISE(ABORT, 'Raw archive is immutable'); END")
            connection.execute(f'PRAGMA user_version={ARCHIVE_VERSION}')
            connection.commit()
        finally:
            connection.close()
        with self._connection(write=True) as db:
            existing = db.execute("SELECT payload FROM checkpoints WHERE key='manager'").fetchone()
            if existing is None:
                original = legacy or {}
                self._document(db, 'legacy-import', original)
                state = self._import_state(db, original)
                self._checkpoint(db, 'manager', state)
                self._checkpoint(db, 'session', state.get('session', {}))
            else:
                state = json.loads(existing[0])
            active = db.execute("SELECT payload FROM checkpoints WHERE key='session'").fetchone()
            if active:
                state['session'] = json.loads(active[0])
            return state

    @staticmethod
    def _checkpoint(db, key: str, payload: dict) -> None:
        db.execute('INSERT INTO checkpoints(key,payload) VALUES (?,?) '
                   'ON CONFLICT(key) DO UPDATE SET payload=excluded.payload', (key, encoded(payload)))

    @staticmethod
    def _document(db, kind: str, value: dict) -> None:
        payload = encoded(value)
        db.execute('INSERT OR IGNORE INTO documents(kind,hash,payload) VALUES (?,?,?)',
                   (kind, digest(payload), payload))

    def _import_state(self, db, original: dict) -> dict:
        state = deepcopy(original)

        def retain(record: dict, fallback: str) -> None:
            points = record.pop('samples', [])
            trace = record.get('trace_id') or fallback
            # Older versions can contain divergent snapshots of one session.
            # Retain both exact series under distinct trace identifiers rather
            # than overwriting, silently choosing one, or blocking migration.
            existing = db.execute('SELECT sample_count FROM traces WHERE id=?', (trace,)).fetchone()
            if existing:
                for seq, point in enumerate(points[:existing[0]]):
                    saved = db.execute('SELECT payload FROM samples WHERE trace_id=? AND seq=?', (trace, seq)).fetchone()
                    if saved is None or saved[0] != encoded(point):
                        trace += ':snapshot:' + digest(encoded(points))
                        break
            self._append(db, trace, points, start=0)
            info = db.execute('SELECT sample_count FROM traces WHERE id=?', (trace,)).fetchone()
            record.update(trace_id=trace, archived_sample_count=info[0])

        for kind, id_key in (('idle_measurements', 'measurement_id'), ('calibrations', 'calibration_id')):
            for index, record in enumerate(state.get(kind, [])):
                retain(record, f'{kind}:{record.get(id_key) or index}')
        for index, record in enumerate(state.get('charge_history', [])):
            session = record.get('session')
            if session:
                retain(session, f"session:{session.get('session_id') or record.get('session_id') or index}")
        session = state.get('session')
        if session:
            retain(session, f"session:{session.get('session_id') or 'legacy-current'}")
        return state

    @staticmethod
    def _append(db, trace: str, points: Iterable[dict], *, start: int | None = None) -> int:
        if not trace:
            raise ValueError('A trace identifier is required')
        db.execute('INSERT OR IGNORE INTO traces(id) VALUES (?)', (trace,))
        count, chain = db.execute('SELECT sample_count,chain_hash FROM traces WHERE id=?', (trace,)).fetchone()
        offset = count if start is None else start
        if offset < 0 or offset > count:
            raise ValueError('Non-contiguous archive write')
        for seq, point in enumerate(points, offset):
            payload = encoded(point)
            if seq < count:
                old = db.execute('SELECT payload FROM samples WHERE trace_id=? AND seq=?', (trace, seq)).fetchone()
                if old is None or old[0] != payload:
                    raise ValueError('Attempt to replace an immutable observation')
                continue
            chain = digest(chain + '\n' + payload)
            db.execute('INSERT INTO samples VALUES (?,?,?,?,?)',
                       (trace, seq, point.get('timestamp'), payload, chain))
            count += 1
        db.execute('UPDATE traces SET sample_count=?,chain_hash=? WHERE id=?', (count, chain, trace))
        return count

    def append_samples(self, trace: str, points: Iterable[dict], *, start: int | None = None,
                       checkpoint: dict | None = None) -> int:
        """Commit observations and their recovery state together; exact retries are idempotent."""
        with self._connection(write=True) as db:
            count = self._append(db, trace, points, start=start)
            if checkpoint is not None:
                self._checkpoint(db, 'session', {**checkpoint, 'trace_id': trace,
                                                'archived_sample_count': count})
            return count

    def append_event(self, trace: str, event: dict) -> None:
        """Retain every receipt, including unchanged/invalid reports and shutdown observations."""
        with self._connection(write=True) as db:
            db.execute('INSERT OR IGNORE INTO traces(id) VALUES (?)', (trace,))
            count = db.execute('SELECT event_count FROM traces WHERE id=?', (trace,)).fetchone()[0]
            db.execute('INSERT INTO events VALUES (?,?,?)', (trace, count, encoded(event)))
            db.execute('UPDATE traces SET event_count=event_count+1 WHERE id=?', (trace,))

    def save_state(self, state: dict) -> None:
        """Append changed metadata/evaluations and replace only derived recovery indexes."""
        with self._connection(write=True) as db:
            self._document(db, 'manager-state', state)
            self._checkpoint(db, 'manager', state)
            if 'session' in state:
                self._checkpoint(db, 'session', state['session'])

    def retain_document(self, kind: str, value: dict) -> None:
        with self._connection(write=True) as db:
            self._document(db, kind, value)

    def read_samples(self, trace: str, start: int = 0, limit: int | None = None) -> list[dict]:
        if start < 0 or (limit is not None and limit < 0):
            raise ValueError('Invalid archive range')
        with self._connection() as db:
            query = 'SELECT payload FROM samples WHERE trace_id=? AND seq>=? ORDER BY seq LIMIT ?'
            return [json.loads(row[0]) for row in db.execute(query, (trace, start, -1 if limit is None else limit))]

    def trace_info(self, trace: str) -> dict:
        with self._connection() as db:
            row = db.execute('SELECT sample_count,chain_hash,event_count FROM traces WHERE id=?', (trace,)).fetchone()
            return dict(trace_id=trace, sample_count=row[0], sha256_chain=row[1], event_count=row[2]) if row else {}

    def verify_trace(self, trace: str) -> bool:
        with self._connection() as db:
            expected = db.execute('SELECT sample_count,chain_hash FROM traces WHERE id=?', (trace,)).fetchone()
            if expected is None:
                return False
            chain, count = '', 0
            for seq, payload, stored in db.execute('SELECT seq,payload,chain_hash FROM samples WHERE trace_id=? ORDER BY seq', (trace,)):
                chain = digest(chain + '\n' + payload)
                if seq != count or chain != stored:
                    return False
                count += 1
            return (count, chain) == expected

    def iter_export(self, metadata: dict) -> Iterator[str]:
        """Stream one consistent SQLite read snapshot, without loading all raw rows in RAM."""
        with self._connection() as db:
            # Establish the WAL read snapshot before returning the first byte.
            db.execute('SELECT count(*) FROM traces').fetchone()
            yield '{'
            for key, value in metadata.items():
                if key != 'raw_archive':
                    yield json.dumps(key) + ':' + encoded(value) + ','
            yield '"raw_archive":{"version":1,"traces":['
            first_trace = True
            for trace, count, chain, event_count in db.execute('SELECT id,sample_count,chain_hash,event_count FROM traces ORDER BY id'):
                if not first_trace:
                    yield ','
                first_trace = False
                header = dict(trace_id=trace, sample_count=count, sha256_chain=chain, event_count=event_count)
                yield encoded(header)[:-1] + ',"samples":['
                first = True
                for (payload,) in db.execute('SELECT payload FROM samples WHERE trace_id=? ORDER BY seq', (trace,)):
                    yield ('' if first else ',') + payload
                    first = False
                yield '],"events":['
                first = True
                for (payload,) in db.execute('SELECT payload FROM events WHERE trace_id=? ORDER BY seq', (trace,)):
                    yield ('' if first else ',') + payload
                    first = False
                yield ']}'
            yield '],"documents":['
            first = True
            for kind, sha, payload in db.execute('SELECT kind,hash,payload FROM documents ORDER BY id'):
                yield ('' if first else ',') + '{"kind":' + encoded(kind) + ',"sha256":' + encoded(sha) + ',"payload":' + payload + '}'
                first = False
            yield ']}}'
