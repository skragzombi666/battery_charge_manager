"""Release metadata must agree with the version sent to the frontend."""

import json
from pathlib import Path
import runpy
import unittest


class VersionTests(unittest.TestCase):
    def test_display_version_matches_manifest(self):
        root = Path(__file__).resolve().parents[1] / "custom_components" / "battery_charge_manager"
        constants = runpy.run_path(str(root / "const.py"))
        manifest = json.loads((root / "manifest.json").read_text())
        self.assertEqual(constants["VERSION"], manifest["version"])

    def test_per_calibration_algorithm_is_versioned(self):
        root = Path(__file__).resolve().parents[1] / "custom_components" / "battery_charge_manager"
        constants = runpy.run_path(str(root / "const.py"))
        self.assertEqual(constants["ALGORITHM_VERSION"], "0.4.0")
