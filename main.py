"""
XJTLU PDF Downloader - Batch Version (Playwright-based)
A GUI tool to batch download PDFs from XJTLU ETD system using browser automation.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from pathlib import Path
import time
from url_parser import parse_viewer_url, validate_url
from downloader import PDFDownloader, format_file_size


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
        
        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


class PDFDownloaderApp:
    """Main application class with Batch GUI."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("XJTLU PDF Batch Downloader (Playwright)")
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
        style.configure('Title.TLabel', font=('Microsoft YaHei UI', 16, 'bold'))
        style.configure('Info.TLabel', font=('Microsoft YaHei UI', 9))
        style.configure('Action.TButton', font=('Microsoft YaHei UI', 10))
        style.configure('Primary.TButton', font=('Microsoft YaHei UI', 11, 'bold'))

    def build_ui(self):
        # Main Padding
        main = ttk.Frame(self.root, padding="20")
        main.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main, text="📚 XJTLU PDF Batch Downloader", style='Title.TLabel').pack(pady=(0, 5))
        ttk.Label(main, text="Add URLs and select save directory for batch download (Playwright-based)", style='Info.TLabel', foreground='gray').pack(pady=(0, 15))
        
        # --- URL List Section ---
        header_frame = ttk.Frame(main)
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="PDF URLs:", style='Info.TLabel', font=('bold')).pack(side=tk.LEFT)
        
        # Scrollable area
        self.scroll_container = ScrollableFrame(main)
        self.scroll_container.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # Controls below list
        controls = ttk.Frame(main)
        controls.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Button(
            controls, 
            text="➕ Add URL", 
            command=self.add_url_field,
            style='Action.TButton'
        ).pack(side=tk.LEFT)
        
        ttk.Button(
            controls,
            text="🗑️ Clear All",
            command=self.clear_urls,
            style='Action.TButton'
        ).pack(side=tk.LEFT, padx=10)

        # --- Output Directory Section ---
        dir_frame = ttk.LabelFrame(main, text="Save Location", padding="10")
        dir_frame.pack(fill=tk.X, pady=(0, 15))
        
        dir_entry = ttk.Entry(dir_frame, textvariable=self.target_dir, state='readonly')
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(
            dir_frame, 
            text="📂 Browse...", 
            command=self.browse_directory
        ).pack(side=tk.RIGHT)

        # --- Options Section ---
        options_frame = ttk.LabelFrame(main, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Checkbutton(
            options_frame,
            text="Headless mode (hide browser window)",
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
        
        self.status_label = ttk.Label(self.progress_frame, text="Ready", style='Info.TLabel')
        self.status_label.pack(anchor=tk.W)

        # --- Main Action Button ---
        self.download_btn = ttk.Button(
            main,
            text="🚀 Start Batch Download",
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
            messagebox.showwarning("Notice", "Please select a save directory first!")
            return
        
        target_path = Path(target_path_str)
        if not target_path.exists():
            try:
                target_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create directory: {e}")
                return

        # 2. Collect Valid URLs
        urls_to_process = []
        for entry in self.url_rows:
            url = entry.get().strip()
            if url:
                urls_to_process.append(url)
        
        if not urls_to_process:
            messagebox.showwarning("Notice", "Please enter at least one URL!")
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
                                self.update_status(f"Processing {idx}/{tot}...", 'blue'))
                
                # Step 1: Validate & Parse
                is_valid, err_msg = validate_url(url)
                if not is_valid:
                    fail_count += 1
                    errors.append(f"URL {current_num}: Invalid format - {err_msg}")
                    continue

                parse_res = parse_viewer_url(url)
                if not parse_res['success']:
                    fail_count += 1
                    errors.append(f"URL {current_num}: Parse failed - {parse_res['error']}")
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
                    errors.append(f"URL {current_num}: Download failed - {result['error']}")
                
                # Update Progress Bar
                progress = (current_num / total_count) * 100
                self.root.after(0, lambda p=progress: self.total_progress_var.set(p))
                
                # Small delay between downloads
                time.sleep(1)
                
        except Exception as e:
            errors.append(f"Batch error: {str(e)}")

        # Finished
        self.is_downloading = False
        
        result_msg = f"Batch complete!\nSuccess: {success_count}\nFailed: {fail_count}"
        if errors:
            result_msg += "\n\nError details:\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                result_msg += "\n..."

        self.root.after(0, lambda: self.download_btn.configure(state='normal'))
        self.root.after(0, lambda: self.update_status("All tasks completed", 'green'))
        self.root.after(0, lambda: messagebox.showinfo("Batch Download Report", result_msg))

    def on_closing(self):
        """Cleanup when window is closed."""
        self.root.destroy()


def main():
    app = PDFDownloaderApp()
    app.root.mainloop()

if __name__ == "__main__":
    main()
