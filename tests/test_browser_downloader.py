import tempfile
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from xjtlu_downloader.infra.browser_downloader import BrowserPDFDownloader


class BrowserDownloaderTests(unittest.TestCase):
    def test_normalize_api_message_handles_json_string(self):
        self.assertEqual(
            BrowserPDFDownloader._normalize_api_message('"非法请求,请登录后访问"'),
            "非法请求,请登录后访问",
        )

    def test_build_api_error_message_forbidden_is_actionable(self):
        message = BrowserPDFDownloader._build_api_error_message(
            403,
            '"非法请求,请登录后访问"',
        )

        self.assertIn("文件接口返回 403", message)
        self.assertIn("请回到 ETD 系统重新打开 PDF 并复制新链接", message)

    def test_session_profile_helpers_manage_profile_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            profile_dir = Path(temp_dir) / "profile"
            downloader = BrowserPDFDownloader(user_data_dir=profile_dir)

            self.assertFalse(downloader.has_session_profile())

            profile_dir.mkdir(parents=True, exist_ok=True)
            (profile_dir / "cookie.txt").write_text("session")
            self.assertTrue(downloader.has_session_profile())

            downloader.clear_session_profile()
            self.assertFalse(downloader.has_session_profile())


if __name__ == "__main__":
    unittest.main()
