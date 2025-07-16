import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

from config import load_config, save_config
from downloader import download
from playlist_info import get_playlist_info
from progress import make_progress_hook
from logic import collect_download_params, validate_params, build_config_for_download
from logger import update_log

import sys
import ctypes

class YTDownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube 视频下载器")
        self.geometry("700x750")
        self.resizable(True, True)
        self.default_font = ("微软雅黑", 11)
        self.option_add("*Font", self.default_font)
        icon_path = os.path.join(os.path.dirname(__file__), "downloader.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
                # 设置任务栏图标
                try:
                    if os.name == 'nt':
                        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('YTDownloader.YTDownloaderApp.v1')
                except Exception as e:
                    print(f"Error setting taskbar icon: {e}")
            except Exception as e:
                print(f"Error setting icon: {e}")
        self.config = load_config()
        self.create_widgets()
        self.load_settings()
        self.downloading = False
        self.download_thread = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()

    def create_widgets(self):
        # 1. 模式选择
        self.mode_var = tk.StringVar(value=self.config.get("mode", "single"))
        ttk.Label(self, text="下载模式:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        ttk.Radiobutton(self, text="单个视频/音频", variable=self.mode_var, value="single", command=self.on_mode_change).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Radiobutton(self, text="播放列表", variable=self.mode_var, value="playlist", command=self.on_mode_change).grid(row=0, column=2, sticky="w", padx=5)

        # 2. URL输入
        ttk.Label(self, text="YouTube链接（每行一个）:").grid(row=1, column=0, sticky="w", padx=10)
        self.url_text = tk.Text(self, height=5, width=60, font=self.default_font)
        self.url_text.grid(row=2, column=0, columnspan=4, sticky="nsew", padx=10)

        # 3. 播放列表选项
        self.playlist_frame = ttk.LabelFrame(self, text="播放列表选项")
        self.playlist_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=10, pady=8)
        ttk.Label(self.playlist_frame, text="范围:").grid(row=0, column=0, padx=5, pady=5)
        self.range_start = ttk.Entry(self.playlist_frame, width=5)
        self.range_start.grid(row=0, column=1, padx=2)
        ttk.Label(self.playlist_frame, text="-").grid(row=0, column=2)
        self.range_end = ttk.Entry(self.playlist_frame, width=5)
        self.range_end.grid(row=0, column=3, padx=2)
        self.info_btn = ttk.Button(self.playlist_frame, text="获取播放列表信息", command=self.on_get_playlist_info)
        self.info_btn.grid(row=0, column=4, padx=8)
        self.playlist_info_label = ttk.Label(self.playlist_frame, text="", foreground="#0078D7")
        self.playlist_info_label.grid(row=1, column=0, columnspan=5, sticky="w", padx=5, pady=3)

        # 4. 下载路径
        ttk.Label(self, text="下载路径:").grid(row=4, column=0, sticky="w", padx=10, pady=8)
        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(self, textvariable=self.path_var, width=40)
        self.path_entry.grid(row=4, column=1, sticky="ew", padx=2)
        ttk.Button(self, text="浏览", command=self.browse_path).grid(row=4, column=2, padx=2)

        # 5. 文件格式（扩展更多格式）
        ttk.Label(self, text="文件格式:").grid(row=5, column=0, sticky="w", padx=10, pady=8)
        self.format_var = tk.StringVar()
        self.format_combo = ttk.Combobox(
            self, textvariable=self.format_var,
            values=["mp4", "mp3", "m4a", "webm", "flac", "wav", "aac", "opus", "mov", "avi"],
            state="readonly", width=12)
        self.format_combo.grid(row=5, column=1, sticky="ew", padx=2)

        # 6. 分辨率选择
        ttk.Label(self, text="分辨率:").grid(row=6, column=0, sticky="w", padx=10)
        self.resolution_var = tk.StringVar()
        self.resolution_combo = ttk.Combobox(
            self, textvariable=self.resolution_var,
            values=["最高", "2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "音频"],
            state="readonly", width=12)
        self.resolution_combo.grid(row=6, column=1, sticky="ew", padx=2)
        self.resolution_combo.set("最高")

        # 7. 码率选择
        ttk.Label(self, text="音频码率:").grid(row=6, column=2, sticky="e", padx=2)
        self.bitrate_var = tk.StringVar()
        self.bitrate_combo = ttk.Combobox(
            self, textvariable=self.bitrate_var,
            values=["默认", "320k", "256k", "192k", "128k", "64k"],
            state="readonly", width=10)
        self.bitrate_combo.grid(row=6, column=3, sticky="ew", padx=2)
        self.bitrate_combo.set("默认")

        # 8. 其它高级选项
        self.subtitle_var = tk.BooleanVar()
        self.cover_var = tk.BooleanVar()
        self.shorten_filename_var = tk.BooleanVar()
        ttk.Checkbutton(self, text="下载字幕", variable=self.subtitle_var).grid(row=7, column=0, sticky="w", padx=10)
        ttk.Checkbutton(self, text="下载封面", variable=self.cover_var).grid(row=7, column=1, sticky="w", padx=2)
        ttk.Checkbutton(self, text="自动缩短文件名", variable=self.shorten_filename_var).grid(row=7, column=2, sticky="w", padx=2)

        # 9. 代理设置
        self.use_proxy_var = tk.BooleanVar()
        self.proxy_check = ttk.Checkbutton(self, text="使用代理", variable=self.use_proxy_var, command=self.on_proxy_toggle)
        self.proxy_check.grid(row=8, column=0, sticky="w", padx=10, pady=8)
        ttk.Label(self, text="代理地址（如 http://127.0.0.1:10808）:").grid(row=8, column=1, sticky="e", padx=2)
        self.proxy_var = tk.StringVar()
        self.proxy_entry = ttk.Entry(self, textvariable=self.proxy_var, width=30)
        self.proxy_entry.grid(row=8, column=2, columnspan=2, sticky="ew", padx=2)

        # 10. Cookie文件
        ttk.Label(self, text="Cookie文件路径:").grid(row=9, column=0, sticky="w", padx=10, pady=8)
        self.cookie_var = tk.StringVar()
        self.cookie_entry = ttk.Entry(self, textvariable=self.cookie_var, width=40)
        self.cookie_entry.grid(row=9, column=1, sticky="ew", padx=2)
        ttk.Button(self, text="浏览", command=self.browse_cookie).grid(row=9, column=2, padx=2)
        self.cookie_entry_tooltip = ttk.Label(self, text="请用浏览器导出Netscape格式的cookie文件", foreground="gray")
        self.cookie_entry_tooltip.grid(row=10, column=1, sticky="w", padx=2)

        # 11. 操作按钮
        self.start_btn = tk.Button(self, text="开始下载", command=self.start_download, bg="#4CAF50", fg="white", activebackground="#388E3C", width=12)
        self.start_btn.grid(row=11, column=0, pady=15)
        self.pause_btn = tk.Button(self, text="暂停下载", state="disabled", bg="#FFA726", fg="white", activebackground="#F57C00", width=12, command=self.pause_download)
        self.pause_btn.grid(row=11, column=1)
        self.cancel_btn = tk.Button(self, text="取消下载", state="disabled", bg="#E57373", fg="white", activebackground="#C62828", width=12, command=self.cancel_download)
        self.cancel_btn.grid(row=11, column=2)

        # 12. 进度条
        self.progressbar = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progressbar.grid(row=12, column=0, columnspan=4, sticky="ew", padx=10, pady=5)

        # 13. 状态/进度
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(self, textvariable=self.status_var, background="#F0F0F0", foreground="#0078D7", anchor="center", font=("微软雅黑", 12, "bold"))
        self.status_label.grid(row=13, column=0, columnspan=4, sticky="ew", padx=10, pady=5)

        # 14. 日志窗口（支持右键菜单）
        self.progress_listbox = tk.Listbox(self, height=12, width=80, font=("Consolas", 10))
        self.progress_listbox.grid(row=14, column=0, columnspan=4, sticky="nsew", padx=10, pady=5)
        self.progress_listbox.bind("<Button-3>", self.show_log_menu)
        self.log_menu = tk.Menu(self, tearoff=0)
        self.log_menu.add_command(label="清空日志", command=self.clear_log)
        self.log_menu.add_command(label="复制全部", command=self.copy_log)

        # 设置grid权重
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(14, weight=2)

        self.on_mode_change()
        self.on_proxy_toggle()

    def show_log_menu(self, event):
        try:
            self.log_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.log_menu.grab_release()

    def clear_log(self):
        self.progress_listbox.delete(0, "end")

    def copy_log(self):
        logs = "\n".join(self.progress_listbox.get(0, "end"))
        self.clipboard_clear()
        self.clipboard_append(logs)

    def load_settings(self):
        self.path_var.set(self.config.get("download_path", ""))
        self.format_var.set(self.config.get("file_format", "mp4"))
        self.use_proxy_var.set(self.config.get("use_proxy", False))
        self.proxy_var.set(self.config.get("proxy_address", ""))
        self.cookie_var.set(self.config.get("cookie_file", ""))
        self.mode_var.set(self.config.get("mode", "single"))
        self.shorten_filename_var.set(self.config.get("shorten_filename", True))

    def save_settings(self):
        self.config["download_path"] = self.path_var.get()
        self.config["file_format"] = self.format_var.get()
        self.config["use_proxy"] = self.use_proxy_var.get()
        self.config["proxy_address"] = self.proxy_var.get()
        self.config["cookie_file"] = self.cookie_var.get()
        self.config["mode"] = self.mode_var.get()
        self.config["shorten_filename"] = self.shorten_filename_var.get()
        save_config(self.config)

    def browse_path(self):
        path = filedialog.askdirectory(title="选择下载文件夹")
        if path:
            self.path_var.set(path)

    def browse_cookie(self):
        path = filedialog.askopenfilename(title="选择Cookie文件", filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if path:
            self.cookie_var.set(path)

    def on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "playlist":
            self.playlist_frame.grid()
        else:
            self.playlist_frame.grid_remove()

    def on_proxy_toggle(self):
        if self.use_proxy_var.get():
            self.proxy_entry.config(state="normal")
        else:
            self.proxy_entry.config(state="disabled")

    def on_get_playlist_info(self):
        url = self.url_text.get("1.0", "end").strip().splitlines()[0]
        if not url:
            messagebox.showerror("错误", "请输入播放列表链接。")
            return
        try:
            info = get_playlist_info(url, self.config)
            self.playlist_info_label.config(text=f"标题: {info['title']} | 视频数: {info['count']}")
        except Exception as e:
            self.playlist_info_label.config(text="获取播放列表信息失败。")

    def start_download(self):
        if self.downloading:
            return
        params = collect_download_params(self)
        valid, errmsg = validate_params(params)
        if not valid:
            self.show_error(errmsg)
            return
        self.save_settings()
        self.downloading = True
        self.status_var.set("正在下载...")
        self.progressbar["value"] = 0
        self.progress_listbox.delete(0, "end")
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.cancel_btn.config(state="normal")
        self._stop_event.clear()
        self._pause_event.clear()
        config_copy = build_config_for_download(self.config, params)
        playlist_range = params["playlist_range"]

        def update_progress(percent, d):
            self.status_var.set(f"下载进度: {percent:.1f}%")
            self.progressbar["value"] = percent
            msg = ""
            if d["status"] == "downloading":
                filename = d.get("filename", "")
                speed = d.get("speed", 0)
                eta = d.get("eta", 0)
                msg = f"{filename} 进度: {percent:.1f}%"
                if speed:
                    msg += f" 速度: {self._format_speed(speed)}"
                if eta:
                    msg += f" 剩余: {self._format_eta(eta)}"
            elif d["status"] == "finished":
                msg = f"{d.get('filename', '')} 下载完成"
            if msg:
                # 只保留每个文件一行进度
                found = False
                for i in range(self.progress_listbox.size()):
                    line = self.progress_listbox.get(i)
                    if d.get("filename", "") and d.get("filename", "") in line:
                        self.progress_listbox.delete(i)
                        self.progress_listbox.insert(i, msg)
                        found = True
                        break
                if not found:
                    self.progress_listbox.insert("end", msg)
                self.progress_listbox.see("end")

        def run_with_retry(retry=2):
            for attempt in range(1, retry+2):
                try:
                    download(params["urls"], config_copy, make_progress_hook(self._wrap_progress(update_progress)), playlist_range, stop_event=self._stop_event, pause_event=self._pause_event)
                    self.status_var.set("下载完成。")
                    break
                except Exception as e:
                    if self._stop_event.is_set():
                        self.status_var.set("下载已取消。")
                        break
                    self.show_error(f"下载失败（第{attempt}次尝试）: {e}")
                    if attempt == retry+1:
                        break
            self.downloading = False
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            self.cancel_btn.config(state="disabled")
        self.download_thread = threading.Thread(target=run_with_retry)
        self.download_thread.start()

    def _wrap_progress(self, func):
        # 处理暂停
        def wrapper(percent, d):
            while self._pause_event.is_set() and not self._stop_event.is_set():
                if not self.downloading:
                    break
                self.status_var.set("已暂停，点击继续下载")
                self.update()
                import time; time.sleep(0.2)
            if not self._stop_event.is_set():
                func(percent, d)
        return wrapper

    def pause_download(self):
        if not self.downloading:
            return
        if not self._pause_event.is_set():
            self._pause_event.set()
            self.pause_btn.config(text="继续下载")
        else:
            self._pause_event.clear()
            self.pause_btn.config(text="暂停下载")

    def cancel_download(self):
        if not self.downloading:
            return
        self._stop_event.set()
        self.status_var.set("正在取消下载...")
        self.pause_btn.config(state="disabled")
        self.cancel_btn.config(state="disabled")
        # 线程会自动检测 _stop_event 并退出
        # 新增：等待线程最多2秒，超时强制提示
        def wait_cancel():
            self.download_thread.join(timeout=2)
            if self.download_thread.is_alive():
                self.status_var.set("取消请求已发送，部分任务可能仍在处理中。")
            else:
                self.status_var.set("下载已取消。")
            self.downloading = False
            self.start_btn.config(state="normal")
            self.pause_btn.config(state="disabled")
            self.cancel_btn.config(state="disabled")
        threading.Thread(target=wait_cancel, daemon=True).start()

    def show_error(self, msg):
        self.status_var.set(msg)
        self.status_label.config(foreground="red")
        update_log(self.progress_listbox, f"[错误] {msg}", error=True)

    def _format_speed(self, speed):
        # speed: bytes/sec
        if speed is None:
            return ""
        units = ["B/s", "KB/s", "MB/s", "GB/s"]
        idx = 0
        while speed >= 1024 and idx < len(units) - 1:
            speed /= 1024
            idx += 1
        return f"{speed:.2f} {units[idx]}"

    def _format_eta(self, eta):
        # eta: seconds
        if eta is None:
            return ""
        m, s = divmod(int(eta), 60)
        h, m = divmod(m, 60)
        if h:
            return f"{h}小时{m}分{s}秒"
        elif m:
            return f"{m}分{s}秒"
        else:
            return f"{s}秒"

if __name__ == "__main__":
    app = YTDownloaderApp()
    app.mainloop()
