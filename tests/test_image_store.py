from __future__ import annotations

import base64
from pathlib import Path
import tempfile
import unittest

from custom_components.battery_charge_manager.image_store import save_uploaded_image


class ImageStoreTests(unittest.TestCase):
    def test_png_upload_is_written_under_www_and_returns_local_path(self) -> None:
        png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZzvAAAAAASUVORK5CYII="
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = save_uploaded_image(
                temp_dir,
                filename="battery.png",
                mime_type="image/png",
                encoded_data=base64.b64encode(png).decode("ascii"),
            )

            self.assertTrue(path.startswith("/local/battery_charge_manager/"))
            relative = path.removeprefix("/local/")
            stored = Path(temp_dir) / "www" / relative
            self.assertTrue(stored.is_file())
            self.assertEqual(stored.read_bytes(), png)

    def test_upload_rejects_unsupported_or_spoofed_image(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(ValueError, "Unsupported image type"):
                save_uploaded_image(
                    temp_dir,
                    filename="image.svg",
                    mime_type="image/svg+xml",
                    encoded_data=base64.b64encode(b"<svg></svg>").decode("ascii"),
                )
            with self.assertRaisesRegex(ValueError, "does not match"):
                save_uploaded_image(
                    temp_dir,
                    filename="fake.png",
                    mime_type="image/png",
                    encoded_data=base64.b64encode(b"not a png").decode("ascii"),
                )


if __name__ == "__main__":
    unittest.main()
