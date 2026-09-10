# Architecture

## Components

- `manager.py`: persistent domain model, sensor tracking, measurement evaluation, endpoint detection, safety, and statistics.
- `models.py`: versioned setup, battery, idle-measurement, calibration, trace-sample, and session records.
- `history.py`: exact-revision applicability, metadata comparison and bounded historical chart data.
- `websocket_api.py`: authenticated frontend read and control API.
- `panel.py`: frontend module serving, custom-card registration, and sidebar-panel registration.
- `frontend/battery-charge-manager.js`: side panel and Lovelace card.
- standard Home Assistant entity platforms: automation-facing controls and measurements.

## Persistence

Data is stored through Home Assistant's `Store` helper. Measurement records retain original setup and battery snapshots. Current calculations accept the original current revision or an explicit approval for the exact current revision pair, then apply validity, source-dependency and quality rules. Approval and validity decisions retain timestamps, actors and reasons. Reanalysis retains previous derived results.

Every sensor event is evaluated. Growing session traces are checkpointed at most once per heartbeat (30 seconds); lifecycle changes and orderly shutdown save immediately. Historical state rows are scoped to the selected profile and omit samples. A separate authenticated detail request returns one record with a bounded, extrema-preserving chart; full samples remain in storage.

## Frontend access

The same JavaScript module defines the full panel and the compact card. The card uses the direct `/battery-charge-manager` route, so it continues to open the panel when the user hides the sidebar entry.

Within the panel, home and management are the two navigation levels. Existing
management forms and history tables remain shared. Separate charge, calibration
and idle live renderers feed both the home page and the corresponding management
page. Quantity, battery, setup and target controls share the existing selection
API; there is no second configuration model. Committed selections explicitly
refresh readiness, while uncommitted form edits retain deferred rendering.

Only calibration disclosure visibility uses browser `localStorage`, keyed by HA
user ID and scoped to the current origin. It defaults closed, survives panel
replacement/upgrades, and falls back to in-memory state if storage is blocked.
It is not synchronized between devices. Setup and charge-target disclosure state
lasts for the current panel instance. The backend remains authoritative for all
charging selections and measurement state.

The header uses HA's `ha-icon-button` public `path`/`label` properties and the
bubbling, composed `hass-toggle-menu` event, the same event emitted by HA's menu
component. It does not set private visibility/context fields or navigate to a
hard-coded dashboard. See the official [HA menu component](https://github.com/home-assistant/frontend/blob/dev/src/components/ha-menu-button.ts)
and [icon control](https://github.com/home-assistant/frontend/blob/dev/src/components/ha-icon-button.ts).

## Safety boundary

The integration controls mains power to an existing charger. It does not implement chemistry-specific charging control. The charger and battery protection electronics remain the primary electrical safety layer.
