"""
Legacy compatibility wrapper for the Playwright downloader.
"""

import sys
from pathlib import Path
from typing import Callable, Optional

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from xjtlu_downloader.core.files import format_file_size
from xjtlu_downloader.infra.browser_downloader import BrowserPDFDownloader


class PDFDownloader(BrowserPDFDownloader):
    """Keep the old dict-based interface while delegating to the new core."""

    def download(
        self,
        viewer_url: str,
        save_path: str,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> dict:
        return super().download(viewer_url, save_path, progress_callback).to_legacy_dict()


if __name__ == "__main__":
    print("PDFDownloader module (Playwright async-based) loaded")
    print("Use download() method - it handles async internally")
