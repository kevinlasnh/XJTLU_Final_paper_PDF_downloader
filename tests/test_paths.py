import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from xjtlu_downloader.core.paths import APP_DIR_NAME, get_app_data_dir, get_browser_profile_dir


class PathTests(unittest.TestCase):
    def test_get_app_data_dir_uses_expected_app_name(self):
        app_dir = get_app_data_dir()

        self.assertEqual(app_dir.name, APP_DIR_NAME)
        self.assertTrue(app_dir.exists())

    def test_get_browser_profile_dir_creates_profile_subdirectory(self):
        profile_dir = get_browser_profile_dir()

        self.assertEqual(profile_dir.name, "playwright-profile")
        self.assertTrue(profile_dir.exists())


if __name__ == "__main__":
    unittest.main()
