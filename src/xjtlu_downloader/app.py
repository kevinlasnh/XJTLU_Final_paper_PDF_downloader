"""Application entry point for the new PySide6 desktop GUI."""

import sys

from PySide6.QtWidgets import QApplication

from xjtlu_downloader.packaging.runtime import configure_runtime_environment
from xjtlu_downloader.ui.main_window import MainWindow


def main() -> int:
    configure_runtime_environment()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
