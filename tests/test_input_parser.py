import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from xjtlu_downloader.core.input_parser import extract_urls_from_text


class InputParserTests(unittest.TestCase):
    def test_extract_urls_from_multiline_text(self):
        text = (
            "foo\n"
            "https://etd.xjtlu.edu.cn/static/readonline/web/viewer.html?file=abc\n"
            "https://example.com/test"
        )

        urls = extract_urls_from_text(text)

        self.assertEqual(
            urls,
            [
                "https://etd.xjtlu.edu.cn/static/readonline/web/viewer.html?file=abc",
                "https://example.com/test",
            ],
        )

    def test_extract_urls_trims_trailing_punctuation(self):
        urls = extract_urls_from_text("see https://etd.xjtlu.edu.cn/viewer.html?file=abc);")

        self.assertEqual(urls, ["https://etd.xjtlu.edu.cn/viewer.html?file=abc"])


if __name__ == "__main__":
    unittest.main()
