import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from xjtlu_downloader.core.files import ensure_unique_filepath, format_file_size


class FileHelperTests(unittest.TestCase):
    def test_ensure_unique_filepath_appends_counter(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            existing = Path(temp_dir) / "paper.pdf"
            existing.write_bytes(b"test")

            candidate = ensure_unique_filepath(existing)

            self.assertEqual(candidate.name, "paper_1.pdf")

    def test_format_file_size_handles_kilobytes(self):
        self.assertEqual(format_file_size(2048), "2.0 KB")


if __name__ == "__main__":
    unittest.main()
