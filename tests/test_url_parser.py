import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from xjtlu_downloader.core.url_parser import parse_viewer_url, validate_url


class UrlParserTests(unittest.TestCase):
    def test_validate_url_accepts_viewer_url(self):
        valid, error = validate_url(
            "https://etd.xjtlu.edu.cn/static/readonline/web/viewer.html?file=abc"
        )

        self.assertTrue(valid)
        self.assertEqual(error, "")

    def test_validate_url_rejects_non_etd_url(self):
        valid, error = validate_url("https://example.com/viewer.html?file=abc")

        self.assertFalse(valid)
        self.assertIn("etd.xjtlu.edu.cn", error)

    def test_parse_viewer_url_extracts_record_and_db_code(self):
        url = (
            "https://etd.xjtlu.edu.cn/static/readonline/web/viewer.html?"
            "file=%2Fapi%2Fv1%2FFile%2FBrowserFile%3FdbCode%3DEXAMXJTLU"
            "%26recordId%3D15798%26dbId%3D3"
        )

        parsed = parse_viewer_url(url)

        self.assertTrue(parsed.success)
        self.assertEqual(parsed.record_id, "15798")
        self.assertEqual(parsed.db_code, "EXAMXJTLU")


if __name__ == "__main__":
    unittest.main()
