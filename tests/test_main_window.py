import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from xjtlu_downloader.ui.main_window import MainWindow


class MainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(["test-main-window", "-platform", "offscreen"])

    def setUp(self):
        self.window = MainWindow()

    def tearDown(self):
        self.window.close()
        self.window.deleteLater()

    def test_add_urls_from_input_extracts_multiple_urls(self):
        self.window.url_input.setText(
            "https://etd.xjtlu.edu.cn/viewer.html?file=one https://etd.xjtlu.edu.cn/viewer.html?file=two"
        )

        self.window._add_urls_from_input()

        self.assertEqual(self.window.task_table.rowCount(), 2)
        self.assertEqual(
            self.window.task_table.item(0, 0).data(Qt.ItemDataRole.UserRole),
            "https://etd.xjtlu.edu.cn/viewer.html?file=one",
        )

    def test_add_urls_skips_duplicate_entries(self):
        first_url = "https://etd.xjtlu.edu.cn/viewer.html?file=one"
        second_url = "https://etd.xjtlu.edu.cn/viewer.html?file=two"

        added, skipped = self.window._add_urls([first_url, second_url, first_url])

        self.assertEqual((added, skipped), (2, 1))
        self.assertEqual(self.window.task_table.rowCount(), 2)

    def test_start_download_auto_adds_pending_input(self):
        self.window.url_input.setText("https://etd.xjtlu.edu.cn/viewer.html?file=pending")
        self.window.download_service.has_saved_session = lambda: False

        with patch.object(
            QMessageBox,
            "warning",
            return_value=QMessageBox.StandardButton.Ok,
        ):
            self.window._start_download()

        self.assertEqual(self.window.task_table.rowCount(), 1)
        self.assertEqual(
            self.window.task_table.item(0, 0).data(Qt.ItemDataRole.UserRole),
            "https://etd.xjtlu.edu.cn/viewer.html?file=pending",
        )

    def test_handle_task_started_preserves_viewer_url(self):
        viewer_url = "https://etd.xjtlu.edu.cn/viewer.html?file=abc"
        self.window._append_pending_url(viewer_url)
        self.window.total_tasks = 1

        self.window._handle_task_started(0, "sample.pdf", "C:/tmp/sample.pdf")

        item = self.window.task_table.item(0, 0)
        self.assertEqual(item.text(), "sample.pdf")
        self.assertEqual(item.data(Qt.ItemDataRole.UserRole), viewer_url)


if __name__ == "__main__":
    unittest.main()
