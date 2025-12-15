"""
XJTLU PDF Downloader - Batch Version (Playwright-based)
A cross-platform GUI tool to batch download PDFs from XJTLU ETD system.
Supports Windows, macOS, and Linux.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import time
import platform
from url_parser import parse_viewer_url, validate_url
from downloader import PDFDownloader, format_file_size

# Platform detection
IS_MACOS = platform.system() == 'Darwin'
IS_WINDOWS = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'


class ScrollableFrame(ttk.Frame):
    """A scrollable frame for holding multiple URL inputs."""
    
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        self.canvas = tk.Canvas(self, height=200)  # Fixed height for the list area
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel (platform-specific)
        if IS_MACOS:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_mac)
        else:
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
            # Linux also uses Button-4/5 for scroll
            self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux_up)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux_down)

    def _on_mousewheel(self, event):
        # Windows
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _on_mousewheel_mac(self, event):
        # macOS - delta is already in the right direction
        self.canvas.yview_scroll(int(-1*event.delta), "units")
    
    def _on_mousewheel_linux_up(self, event):
        self.canvas.yview_scroll(-1, "units")
    
    def _on_mousewheel_linux_down(self, event):
        self.canvas.yview_scroll(1, "units")


class PDFDownloaderApp:
    """Main application class with Batch GUI."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("XJTLU 期末试卷下载器")
        self.root.geometry("700x650")
        self.root.minsize(600, 550)
        
        try:
            self.root.iconbitmap(default='')
        except:
            pass
            
        self.downloader = None  # Not used anymore, kept for compatibility
        self.is_downloading = False
        self.url_rows = []  # List of entry widgets
        self.target_dir = tk.StringVar()
        self.headless_var = tk.BooleanVar(value=True)
        
        self.setup_styles()
        self.build_ui()
        self.center_window()
        
        # Add initial URL field
        self.add_url_field()
        
        # Cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_styles(self):
        style = ttk.Style()
        
        # Cross-platform font selection
        if IS_MACOS:
            title_font = ('SF Pro Display', 16, 'bold')
            info_font = ('SF Pro Text', 11)
            action_font = ('SF Pro Text', 12)
            primary_font = ('SF Pro Text', 13, 'bold')
        elif IS_WINDOWS:
            title_font = ('Microsoft YaHei UI', 16, 'bold')
            info_font = ('Microsoft YaHei UI', 9)
            action_font = ('Microsoft YaHei UI', 10)
            primary_font = ('Microsoft YaHei UI', 11, 'bold')
        else:  # Linux
            title_font = ('DejaVu Sans', 14, 'bold')
            info_font = ('DejaVu Sans', 9)
            action_font = ('DejaVu Sans', 10)
            primary_font = ('DejaVu Sans', 11, 'bold')
        
        style.configure('Title.TLabel', font=title_font)
        style.configure('Info.TLabel', font=info_font)
        style.configure('Action.TButton', font=action_font)
        style.configure('Primary.TButton', font=primary_font)
        
        # macOS native theme
        if IS_MACOS:
            try:
                style.theme_use('aqua')
            except:
                pass

    def build_ui(self):
        # Main Padding
        main = ttk.Frame(self.root, padding="20")
        main.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main, text="📚 XJTLU 期末试卷下载器", style='Title.TLabel').pack(pady=(0, 5))
        ttk.Label(main, text="添加PDF链接，选择保存目录，一键批量下载", style='Info.TLabel', foreground='gray').pack(pady=(0, 15))
        
        # --- URL List Section ---
        header_frame = ttk.Frame(main)
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="PDF链接列表:", style='Info.TLabel', font=('bold')).pack(side=tk.LEFT)
        
        # Scrollable area
        self.scroll_container = ScrollableFrame(main)
        self.scroll_container.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Controls below list
        controls = ttk.Frame(main)
        controls.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(
            controls, 
            text="➕ 添加链接", 
            command=self.add_url_field,
            style='Action.TButton'
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            controls,
            text="🗑️ 清空全部",
            command=self.clear_urls,
            style='Action.TButton'
        ).pack(side=tk.LEFT, padx=10)

        # --- Output Directory Section ---
        dir_frame = ttk.LabelFrame(main, text="保存位置", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 15))
        
        dir_entry = ttk.Entry(dir_frame, textvariable=self.target_dir, state='readonly')
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(
            dir_frame, 
            text="📂 浏览...", 
            command=self.browse_directory
        ).pack(side=tk.RIGHT)

        # --- Options Section ---
        options_frame = ttk.LabelFrame(main, text="设置", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Checkbutton(
            options_frame,
            text="后台模式（隐藏浏览器窗口）",
            variable=self.headless_var
        ).pack(anchor=tk.W)

        # --- Progress & Status ---
        self.progress_frame = ttk.Frame(main)
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Total progress
        self.total_progress_var = tk.DoubleVar()
        self.total_progress = ttk.Progressbar(
            self.progress_frame, 
            variable=self.total_progress_var, 
            maximum=100
        )
        self.total_progress.pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = ttk.Label(self.progress_frame, text="就绪，等待开始...", style='Info.TLabel')
        self.status_label.pack(anchor=tk.W)

        # --- Main Action Button ---
        self.download_btn = ttk.Button(
            main,
            text="🚀 开始批量下载",
            style='Primary.TButton',
            command=self.start_batch_download
        )
        self.download_btn.pack(fill=tk.X, ipady=5)

    def add_url_field(self):
        """Add a new row for URL input."""
        row_frame = ttk.Frame(self.scroll_container.scrollable_frame)
        row_frame.pack(fill=tk.X, pady=2)
        
        # Entry
        entry = ttk.Entry(row_frame, font=('Consolas', 9))
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Paste Button
        paste_btn = ttk.Button(
            row_frame, 
            text="📋", 
            width=3,
            command=lambda e=entry: self.paste_to_entry(e)
        )
        paste_btn.pack(side=tk.LEFT, padx=(0, 2))

        # Remove Button
        remove_btn = ttk.Button(row_frame, text="❌", width=3)
        remove_btn.configure(command=lambda: self.remove_url_row(row_frame, entry))
        remove_btn.pack(side=tk.RIGHT)
        
        self.url_rows.append(entry)
        entry.focus_set()

    def paste_to_entry(self, entry_widget):
        try:
            text = self.root.clipboard_get()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, text)
        except:
            pass

    def remove_url_row(self, frame, entry):
        if entry in self.url_rows:
            self.url_rows.remove(entry)
        frame.destroy()

    def clear_urls(self):
        for widget in self.scroll_container.scrollable_frame.winfo_children():
            widget.destroy()
        self.url_rows.clear()
        self.add_url_field()

    def browse_directory(self):
        path = filedialog.askdirectory(title="Select Save Directory")
        if path:
            self.target_dir.set(path)

    def center_window(self):
        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth()//2) - (w//2)
        y = (self.root.winfo_screenheight()//2) - (h//2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')

    def get_unique_filepath(self, directory: Path, filename: str) -> Path:
        """Ensure file path is unique by appending counter if needed."""
        file_path = directory / filename
        stem = file_path.stem
        suffix = file_path.suffix
        counter = 1
        
        while file_path.exists():
            file_path = directory / f"{stem}_{counter}{suffix}"
            counter += 1
        return file_path

    def start_batch_download(self):
        if self.is_downloading:
            return

        # 1. Validate Target Directory
        target_path_str = self.target_dir.get()
        if not target_path_str:
            messagebox.showwarning("提示", "请先选择保存目录！\n\n点击\u201c浏览...\u201d按钮选择你想要保存PDF的文件夹")
            return
        
        target_path = Path(target_path_str)
        if not target_path.exists():
            try:
                target_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建目录：{e}\n\n请检查路径是否正确，或选择其他位置")
                return

        # 2. Collect Valid URLs
        urls_to_process = []
        for entry in self.url_rows:
            url = entry.get().strip()
            if url:
                urls_to_process.append(url)
        
        if not urls_to_process:
            messagebox.showwarning("提示", "请至少输入一个URL链接！\n\n点击\u201c添加链接\u201d按钮，然后粘贴从浏览器复制的PDF链接")
            return

        # 3. Start Thread
        self.is_downloading = True
        self.download_btn.configure(state='disabled')
        self.total_progress['value'] = 0
        
        threading.Thread(
            target=self.process_batch,
            args=(urls_to_process, target_path),
            daemon=True
        ).start()

    def update_status(self, text, color='black'):
        self.status_label.configure(text=text, foreground=color)

    def process_batch(self, urls, save_dir):
        total_count = len(urls)
        success_count = 0
        fail_count = 0
        errors = []

        # Create downloader instance for this batch (each download creates its own event loop)
        headless = self.headless_var.get()
        downloader = PDFDownloader(headless=headless)

        try:
            for index, url in enumerate(urls):
                current_num = index + 1
                self.root.after(0, lambda idx=current_num, tot=total_count: 
                                self.update_status(f"正在处理 {idx}/{tot}...", 'blue'))
                
                # Step 1: Validate & Parse
                is_valid, err_msg = validate_url(url)
                if not is_valid:
                    fail_count += 1
                    errors.append(f"第{current_num}个链接: {err_msg}")
                    continue

                parse_res = parse_viewer_url(url)
                if not parse_res['success']:
                    fail_count += 1
                    errors.append(f"第{current_num}个链接: {parse_res['error']}")
                    continue

                # Step 2: Determine Filename
                suggested_name = downloader.get_suggested_filename(
                    parse_res['viewer_url'],
                    parse_res['record_id']
                )
                final_path = self.get_unique_filepath(save_dir, suggested_name)

                # Step 3: Download via Playwright (async internally)
                def progress_cb(msg, idx=current_num, tot=total_count):
                    self.root.after(0, lambda: self.update_status(f"[{idx}/{tot}] {msg}", 'blue'))
                
                result = downloader.download(
                    parse_res['viewer_url'], 
                    str(final_path),
                    progress_callback=progress_cb
                )
                
                if result['success']:
                    success_count += 1
                else:
                    fail_count += 1
                    errors.append(f"第{current_num}个链接下载失败: {result['error']}")
                
                # Update Progress Bar
                progress = (current_num / total_count) * 100
                self.root.after(0, lambda p=progress: self.total_progress_var.set(p))
                
                # Small delay between downloads
                time.sleep(1)
                
        except Exception as e:
            errors.append(f"批量处理出错: {str(e)}")

        # Finished
        self.is_downloading = False
        
        result_msg = f"批量下载完成！\n\n✅ 成功: {success_count} 个\n❌ 失败: {fail_count} 个"
        if errors:
            result_msg += "\n\n—————— 错误详情 ——————\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                result_msg += f"\n...还有{len(errors)-5}个错误未显示"
        
        # Add VPN tip if there are timeout errors
        if any('超时' in e or 'timeout' in e.lower() for e in errors):
            result_msg += "\n\n❗ 提示：如频繁超时，请关闭VPN/梯子/代理后重试"

        self.root.after(0, lambda: self.download_btn.configure(state='normal'))
        self.root.after(0, lambda: self.update_status("全部任务已完成", 'green'))
        self.root.after(0, lambda: messagebox.showinfo("批量下载报告", result_msg))

    def on_closing(self):
        """Cleanup when window is closed."""
        self.root.destroy()


def main():
    app = PDFDownloaderApp()
    app.root.mainloop()

if __name__ == "__main__":
    main()
