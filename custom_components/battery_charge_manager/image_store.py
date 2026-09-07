"""Store user-uploaded Battery Charge Manager images safely under /config/www."""

from __future__ import annotations

import base64
import binascii
from pathlib import Path
from uuid import uuid4

MAX_IMAGE_BYTES = 3 * 1024 * 1024
_ALLOWED_TYPES = {
    "image/jpeg": (".jpg", lambda data: data.startswith(b"\xff\xd8\xff")),
    "image/png": (".png", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
    "image/webp": (
        ".webp",
        lambda data: len(data) >= 12
        and data.startswith(b"RIFF")
        and data[8:12] == b"WEBP",
    ),
}


def save_uploaded_image(
    config_dir: str | Path,
    *,
    filename: str,
    mime_type: str,
    encoded_data: str,
) -> str:
    """Validate and store an uploaded image, returning its /local path."""
    del filename  # User filenames are never used for filesystem paths.
    spec = _ALLOWED_TYPES.get(str(mime_type).lower())
    if spec is None:
        raise ValueError("Unsupported image type")
    try:
        data = base64.b64decode(encoded_data, validate=True)
    except (binascii.Error, ValueError) as err:
        raise ValueError("Invalid image data") from err
    if not data:
        raise ValueError("Image is empty")
    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError("Image is larger than 3 MB")
    extension, signature_check = spec
    if not signature_check(data):
        raise ValueError("Image content does not match declared image type")

    directory = Path(config_dir) / "www" / "battery_charge_manager"
    directory.mkdir(parents=True, exist_ok=True)
    generated_name = f"{uuid4().hex}{extension}"
    target = directory / generated_name
    target.write_bytes(data)
    return f"/local/battery_charge_manager/{generated_name}"
