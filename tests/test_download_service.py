import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from xjtlu_downloader.core.download_service import DownloadService


class DownloadServiceTests(unittest.TestCase):
    def test_prepare_download_builds_filename_from_parsed_metadata(self):
        service = DownloadService(headless=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            prepared = service.prepare_download(
                (
                    "https://etd.xjtlu.edu.cn/static/readonline/web/viewer.html?"
                    "file=%2Fapi%2Fv1%2FFile%2FBrowserFile%3FdbCode%3DEXAMXJTLU%26recordId%3D12"
                ),
                Path(temp_dir),
            )

            self.assertEqual(prepared.filename, "EXAMXJTLU_12.pdf")
            self.assertEqual(prepared.save_path.name, "EXAMXJTLU_12.pdf")

    def test_prepare_download_rejects_invalid_url(self):
        service = DownloadService(headless=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                service.prepare_download("https://example.com/file.pdf", Path(temp_dir))


if __name__ == "__main__":
    unittest.main()
