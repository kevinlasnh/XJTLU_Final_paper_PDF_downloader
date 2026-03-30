"""Main PySide6 window for the desktop downloader."""

from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QProgressBar,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from xjtlu_downloader.core.input_parser import extract_urls_from_text
from xjtlu_downloader.core.download_service import DownloadService


class DownloadWorker(QThread):
    """Background worker used by the desktop window."""

    task_started = Signal(int, str, str)
    task_progress = Signal(int, str)
    task_finished = Signal(int, dict)
    batch_finished = Signal(dict)

    def __init__(self, viewer_urls: list[str], output_dir: Path, headless: bool = True):
        super().__init__()
        self.viewer_urls = viewer_urls
        self.output_dir = output_dir
        self.headless = headless

    def run(self) -> None:
        service = DownloadService(headless=self.headless)
        success_count = 0
        fail_count = 0

        for index, viewer_url in enumerate(self.viewer_urls):
            try:
                prepared = service.prepare_download(viewer_url, self.output_dir)
                self.task_started.emit(index, prepared.filename, str(prepared.save_path))
                result = service.download_prepared(
                    prepared,
                    progress_callback=lambda message, idx=index: self.task_progress.emit(idx, message),
                )
                result_dict = result.to_legacy_dict()
            except Exception as exc:
                result_dict = {
                    "success": False,
                    "file_path": None,
                    "file_size": 0,
                    "error": str(exc),
                }

            if result_dict.get("success"):
                success_count += 1
            else:
                fail_count += 1

            self.task_finished.emit(index, result_dict)

        self.batch_finished.emit(
            {
                "success_count": success_count,
                "fail_count": fail_count,
                "total_count": len(self.viewer_urls),
            }
        )


class LoginWorker(QThread):
    """Background worker that opens the persistent login browser."""

    progress = Signal(str)
    finished = Signal(dict)

    def run(self) -> None:
        service = DownloadService(headless=False)
        result = service.open_login_browser(progress_callback=self.progress.emit)
        self.finished.emit(result.to_legacy_dict())


class MainWindow(QMainWindow):
    """Minimal but structured PySide6 main window."""

    def __init__(self):
        super().__init__()
        self.download_service = DownloadService(headless=True)
        self.worker = None
        self.login_worker = None
        self.total_tasks = 0
        self.completed_tasks = 0
        self.setWindowTitle("XJTLU 期末试卷下载器")
        self.resize(920, 640)
        self._build_ui()
        self._refresh_session_status()

    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("XJTLU 期末试卷下载器")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        subtitle = QLabel("桌面版重构骨架：服务层已解耦，后续会扩展为完整任务队列。")
        subtitle.setStyleSheet("color: #5f6b76;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        session_row = QHBoxLayout()
        self.session_status_label = QLabel()
        self.session_status_label.setWordWrap(True)
        self.login_button = QPushButton("登录 ETD")
        self.login_button.clicked.connect(self._start_login_flow)
        self.reset_session_button = QPushButton("重置会话")
        self.reset_session_button.clicked.connect(self._reset_session)
        session_row.addWidget(self.session_status_label, 1)
        session_row.addWidget(self.login_button)
        session_row.addWidget(self.reset_session_button)
        layout.addLayout(session_row)

        url_label = QLabel("添加 PDF 查看器链接")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("粘贴一条 viewer URL 后直接按 Enter，或点“粘贴并添加”批量导入。")
        self.url_input.setClearButtonEnabled(True)
        self.url_input.setToolTip("支持直接回车添加；如果直接点“开始下载”，当前输入也会自动加入任务列表。")
        self.url_input.returnPressed.connect(self._add_urls_from_input)
        layout.addWidget(url_label)
        layout.addWidget(self.url_input)

        input_buttons = QHBoxLayout()
        self.add_url_button = QPushButton("添加链接")
        self.add_url_button.clicked.connect(self._add_urls_from_input)
        self.paste_button = QPushButton("粘贴并添加")
        self.paste_button.clicked.connect(self._add_urls_from_clipboard)
        self.remove_button = QPushButton("移除选中")
        self.remove_button.clicked.connect(self._remove_selected_rows)
        self.clear_button = QPushButton("清空列表")
        self.clear_button.clicked.connect(self._clear_task_table)
        input_buttons.addWidget(self.add_url_button)
        input_buttons.addWidget(self.paste_button)
        input_buttons.addWidget(self.remove_button)
        input_buttons.addWidget(self.clear_button)
        input_buttons.addStretch(1)
        layout.addLayout(input_buttons)

        dir_row = QHBoxLayout()
        self.output_dir_input = QLineEdit(str((Path.cwd() / "downloads").resolve()))
        browse_button = QPushButton("选择目录")
        browse_button.clicked.connect(self._browse_output_dir)
        dir_row.addWidget(QLabel("保存目录"))
        dir_row.addWidget(self.output_dir_input, 1)
        dir_row.addWidget(browse_button)
        layout.addLayout(dir_row)

        button_row = QHBoxLayout()
        self.start_button = QPushButton("开始下载")
        self.start_button.clicked.connect(self._start_download)
        self.start_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.open_dir_button = QPushButton("打开目录")
        self.open_dir_button.clicked.connect(self._browse_output_dir)
        button_row.addWidget(self.start_button)
        button_row.addWidget(self.open_dir_button)
        button_row.addStretch(1)
        layout.addLayout(button_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("就绪")
        layout.addWidget(self.status_label)

        self.task_table = QTableWidget(0, 4)
        self.task_table.setHorizontalHeaderLabels(["文件名", "状态", "目标路径", "备注"])
        self.task_table.horizontalHeader().setStretchLastSection(True)
        self.task_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.task_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.task_table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self.task_table, 1)

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("运行日志会显示在这里。")
        self.log_output.setMinimumHeight(160)
        layout.addWidget(self.log_output)

    def _refresh_session_status(self) -> None:
        profile_dir = self.download_service.get_session_profile_dir()
        if self.download_service.has_saved_session():
            self.session_status_label.setText(
                f"会话状态：已检测到程序登录会话。\n会话目录：{profile_dir}"
            )
        else:
            self.session_status_label.setText(
                f"会话状态：尚未检测到程序登录会话。\n请先点击“登录 ETD”，在程序浏览器中完成登录。\n会话目录：{profile_dir}"
            )

    def _set_busy_state(self, busy: bool) -> None:
        self.start_button.setEnabled(not busy)
        self.open_dir_button.setEnabled(not busy)
        self.login_button.setEnabled(not busy)
        self.reset_session_button.setEnabled(not busy)
        self.add_url_button.setEnabled(not busy)
        self.paste_button.setEnabled(not busy)
        self.remove_button.setEnabled(not busy)
        self.clear_button.setEnabled(not busy)
        self.url_input.setEnabled(not busy)

    def _create_filename_item(self, label: str, viewer_url: str) -> QTableWidgetItem:
        item = QTableWidgetItem(label)
        item.setData(Qt.ItemDataRole.UserRole, viewer_url)
        return item

    def _iter_task_urls(self) -> list[str]:
        urls = []
        for row in range(self.task_table.rowCount()):
            item = self.task_table.item(row, 0)
            if not item:
                continue

            viewer_url = item.data(Qt.ItemDataRole.UserRole)
            if viewer_url:
                urls.append(viewer_url)

        return urls

    def _existing_task_urls(self) -> set[str]:
        return set(self._iter_task_urls())

    def _append_pending_url(self, viewer_url: str) -> None:
        row = self.task_table.rowCount()
        self.task_table.insertRow(row)

        self.task_table.setItem(row, 0, self._create_filename_item("待解析", viewer_url))
        self.task_table.setItem(row, 1, QTableWidgetItem("待开始"))
        self.task_table.setItem(row, 2, QTableWidgetItem(""))
        self.task_table.setItem(row, 3, QTableWidgetItem(viewer_url))

    def _add_urls(self, urls: list[str]) -> tuple[int, int]:
        added = 0
        skipped = 0
        existing_urls = self._existing_task_urls()

        for viewer_url in urls:
            if viewer_url in existing_urls:
                skipped += 1
                continue

            self._append_pending_url(viewer_url)
            existing_urls.add(viewer_url)
            added += 1

        return added, skipped

    def _add_urls_from_input(self) -> None:
        raw_text = self.url_input.text().strip()
        if not raw_text:
            return

        urls = extract_urls_from_text(raw_text)
        if not urls and raw_text:
            urls = [raw_text]

        added, skipped = self._add_urls(urls)
        self.url_input.clear()
        if added:
            self._append_log(f"已添加 {added} 条链接到任务列表。")
        if skipped:
            self._append_log(f"已跳过 {skipped} 条重复链接。")
        if not added and not skipped:
            QMessageBox.warning(self, "无法识别链接", "当前输入中没有识别到可用的 URL。")

    def _add_urls_from_clipboard(self) -> None:
        clipboard_text = QApplication.clipboard().text().strip()
        if not clipboard_text:
            QMessageBox.warning(self, "剪贴板为空", "剪贴板中没有可导入的内容。")
            return

        urls = extract_urls_from_text(clipboard_text)
        if not urls:
            QMessageBox.warning(self, "无法识别链接", "剪贴板中没有识别到可用的 URL。")
            return

        added, skipped = self._add_urls(urls)
        if added:
            self._append_log(f"已从剪贴板导入 {added} 条链接。")
        if skipped:
            self._append_log(f"剪贴板中的 {skipped} 条重复链接已跳过。")

    def _remove_selected_rows(self) -> None:
        selected_rows = sorted({index.row() for index in self.task_table.selectedIndexes()}, reverse=True)
        if not selected_rows:
            return

        for row in selected_rows:
            self.task_table.removeRow(row)

        self._append_log(f"已移除 {len(selected_rows)} 条待处理链接。")

    def _clear_task_table(self) -> None:
        if self.task_table.rowCount() == 0:
            return

        self.task_table.setRowCount(0)
        self._append_log("已清空任务列表。")

    def _browse_output_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择保存目录",
            self.output_dir_input.text() or str(Path.cwd()),
        )
        if directory:
            self.output_dir_input.setText(directory)

    def _append_log(self, message: str) -> None:
        self.log_output.appendPlainText(message)
        self.status_label.setText(message)

    def _start_login_flow(self) -> None:
        instructions = (
            "程序将打开一个独立的浏览器会话。\n\n"
            "请在打开的浏览器窗口中完成 ETD 登录，然后关闭整个浏览器窗口。"
            "关闭后，程序会复用这份登录态进行下载。"
        )
        QMessageBox.information(self, "登录 ETD", instructions)
        self._append_log("准备打开程序登录浏览器。")
        self._set_busy_state(True)

        self.login_worker = LoginWorker()
        self.login_worker.progress.connect(self._handle_login_progress)
        self.login_worker.finished.connect(self._handle_login_finished)
        self.login_worker.start()

    def _handle_login_progress(self, message: str) -> None:
        self._append_log(message)

    def _handle_login_finished(self, result: dict) -> None:
        self._set_busy_state(False)
        self._refresh_session_status()

        message = result.get("message") or "登录流程已结束。"
        self._append_log(message)

        if result.get("success"):
            QMessageBox.information(self, "会话已更新", message)
        else:
            QMessageBox.warning(self, "登录流程结束", message)

    def _reset_session(self) -> None:
        answer = QMessageBox.question(
            self,
            "重置会话",
            "这会删除程序保存的 ETD 登录会话。确定继续吗？",
        )
        if answer != QMessageBox.StandardButton.Yes:
            return

        self.download_service.clear_session()
        self._refresh_session_status()
        self._append_log("已重置程序登录会话。")
        QMessageBox.information(self, "会话已重置", "程序登录会话已清除。下次下载前请重新点击“登录 ETD”。")

    def _start_download(self) -> None:
        if self.url_input.text().strip():
            self._add_urls_from_input()

        urls = self._iter_task_urls()

        if not urls:
            QMessageBox.warning(self, "缺少链接", "请先添加至少一个 PDF 查看器链接到任务列表。")
            return

        if not self.download_service.has_saved_session():
            QMessageBox.warning(
                self,
                "缺少登录会话",
                "尚未检测到程序登录会话。\n请先点击“登录 ETD”，在程序浏览器中完成登录后再下载。",
            )
            return

        output_dir = Path(self.output_dir_input.text().strip()).expanduser()
        self.total_tasks = len(urls)
        self.completed_tasks = 0

        for index in range(len(urls)):
            filename_item = self.task_table.item(index, 0)
            if filename_item:
                viewer_url = filename_item.data(Qt.ItemDataRole.UserRole)
            else:
                viewer_url = ""
                filename_item = self._create_filename_item("待解析", viewer_url)

            self.task_table.setItem(index, 0, filename_item)
            self.task_table.setItem(index, 1, QTableWidgetItem("排队中"))
            self.task_table.setItem(index, 2, QTableWidgetItem(str(output_dir)))
            self.task_table.setItem(index, 3, QTableWidgetItem("等待处理"))

        self._set_busy_state(True)
        self.progress_bar.show()
        self.progress_bar.setRange(0, self.total_tasks)
        self.progress_bar.setValue(0)
        self._append_log("已启动下载任务。")

        self.worker = DownloadWorker(urls, output_dir, headless=True)
        self.worker.task_started.connect(self._handle_task_started)
        self.worker.task_progress.connect(self._handle_task_progress)
        self.worker.task_finished.connect(self._handle_task_finished)
        self.worker.batch_finished.connect(self._handle_batch_finished)
        self.worker.start()

    def _handle_task_started(self, row: int, filename: str, save_path: str) -> None:
        existing_item = self.task_table.item(row, 0)
        viewer_url = existing_item.data(Qt.ItemDataRole.UserRole) if existing_item else ""
        self.task_table.setItem(row, 0, self._create_filename_item(filename, viewer_url))
        self.task_table.setItem(row, 1, QTableWidgetItem("运行中"))
        self.task_table.setItem(row, 2, QTableWidgetItem(save_path))
        self.task_table.setItem(row, 3, QTableWidgetItem("浏览器任务已启动"))
        self._append_log(f"[{row + 1}/{self.total_tasks}] 开始处理 {filename}")

    def _handle_task_progress(self, row: int, message: str) -> None:
        self.task_table.setItem(row, 1, QTableWidgetItem("运行中"))
        self.task_table.setItem(row, 3, QTableWidgetItem(message))
        self._append_log(f"[{row + 1}/{self.total_tasks}] {message}")

    def _handle_task_finished(self, row: int, result: dict) -> None:
        self.completed_tasks += 1
        self.progress_bar.setValue(self.completed_tasks)
        if result.get("success"):
            self.task_table.setItem(row, 1, QTableWidgetItem("成功"))
            self.task_table.setItem(row, 2, QTableWidgetItem(result.get("file_path") or ""))
            self.task_table.setItem(row, 3, QTableWidgetItem("下载完成"))
            self._append_log(f"[{row + 1}/{self.total_tasks}] 下载完成。")
            return

        error = result.get("error") or "未知错误"
        self.task_table.setItem(row, 1, QTableWidgetItem("失败"))
        self.task_table.setItem(row, 3, QTableWidgetItem(error))
        self._append_log(f"[{row + 1}/{self.total_tasks}] 下载失败：{error}")

    def _handle_batch_finished(self, summary: dict) -> None:
        self.progress_bar.hide()
        self._set_busy_state(False)
        self._refresh_session_status()
        message = (
            f"批量任务结束。成功 {summary['success_count']} 个，"
            f"失败 {summary['fail_count']} 个，共 {summary['total_count']} 个。"
        )
        self._append_log(message)

        if summary["fail_count"]:
            QMessageBox.warning(self, "批量下载完成", message)
        else:
            QMessageBox.information(self, "批量下载完成", message)
