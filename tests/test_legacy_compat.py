import unittest

from downloader import PDFDownloader, format_file_size
from url_parser import parse_viewer_url, validate_url


class LegacyCompatTests(unittest.TestCase):
    def test_legacy_validate_url_keeps_tuple_api(self):
        valid, error = validate_url(
            "https://etd.xjtlu.edu.cn/static/readonline/web/viewer.html?file=abc"
        )

        self.assertTrue(valid)
        self.assertEqual(error, "")

    def test_legacy_parse_viewer_url_keeps_dict_api(self):
        result = parse_viewer_url(
            "https://etd.xjtlu.edu.cn/static/readonline/web/viewer.html?"
            "file=%2Fapi%2Fv1%2FFile%2FBrowserFile%3FdbCode%3DEXAMXJTLU%26recordId%3D1"
        )

        self.assertIsInstance(result, dict)
        self.assertEqual(result["record_id"], "1")

    def test_legacy_downloader_type_still_exists(self):
        downloader = PDFDownloader(headless=True)

        self.assertTrue(hasattr(downloader, "download"))
        self.assertEqual(format_file_size(1024), "1.0 KB")


if __name__ == "__main__":
    unittest.main()
