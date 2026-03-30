"""Development launcher for the new PySide6 desktop GUI."""

import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from xjtlu_downloader.app import main


if __name__ == "__main__":
    raise SystemExit(main())
