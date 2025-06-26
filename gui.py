import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

from config import load_config, save_config
from downloader import download
from playlist_info import get_playlist_info
from progress import make_progress_hook

class YTDownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube 视频下载器")
        self.geometry("600x650")
        self.resizable(True, True)  # 允许调整窗口大小
        # 设置字体
        self.default_font = ("微软雅黑", 11)
        self.option_add("*Font", self.default_font)
        # 设置窗口图标（如有icon.ico）
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
        self.config = load_config()
        self.create_widgets()
        self.load_settings()
        self.downloading = False
        self.download_thread = None

    def create_widgets(self):
        # 1. 模式选择
        self.mode_var = tk.StringVar(value=self.config.get("mode", "single"))
        ttk.Label(self, text="下载模式:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
        ttk.Radiobutton(self, text="单个视频/音频", variable=self.mode_var, value="single", command=self.on_mode_change).grid(row=0, column=1, sticky="w", padx=5)
        ttk.Radiobutton(self, text="播放列表", variable=self.mode_var, value="playlist", command=self.on_mode_change).grid(row=0, column=2, sticky="w", padx=5)

        # 2. URL输入
        ttk.Label(self, text="YouTube链接（每行一个）:").grid(row=1, column=0, sticky="w", padx=10)
        self.url_text = tk.Text(self, height=5, width=50, font=self.default_font)
        self.url_text.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=10)

        # 3. 播放列表选项
        self.playlist_frame = ttk.LabelFrame(self, text="播放列表选项")
        self.playlist_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=10, pady=8)
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

        # 5. 文件格式
        ttk.Label(self, text="文件格式:").grid(row=5, column=0, sticky="w", padx=10, pady=8)
        self.format_var = tk.StringVar()
        self.format_combo = ttk.Combobox(self, textvariable=self.format_var, values=["mp4", "mp3", "m4a", "webm"], state="readonly", width=10)
        self.format_combo.grid(row=5, column=1, sticky="ew", padx=2)

        # 6. 代理设置
        self.use_proxy_var = tk.BooleanVar()
        self.proxy_check = ttk.Checkbutton(self, text="使用代理", variable=self.use_proxy_var, command=self.on_proxy_toggle)
        self.proxy_check.grid(row=6, column=0, sticky="w", padx=10, pady=8)
        ttk.Label(self, text="代理地址（如 http://127.0.0.1:10808）:").grid(row=6, column=1, sticky="e", padx=2)
        self.proxy_var = tk.StringVar()
        self.proxy_entry = ttk.Entry(self, textvariable=self.proxy_var, width=30)
        self.proxy_entry.grid(row=6, column=2, sticky="ew", padx=2)

        # 7. Cookie文件
        ttk.Label(self, text="Cookie文件路径:").grid(row=7, column=0, sticky="w", padx=10, pady=8)
        self.cookie_var = tk.StringVar()
        self.cookie_entry = ttk.Entry(self, textvariable=self.cookie_var, width=40)
        self.cookie_entry.grid(row=7, column=1, sticky="ew", padx=2)
        ttk.Button(self, text="浏览", command=self.browse_cookie).grid(row=7, column=2, padx=2)
        self.cookie_entry_tooltip = ttk.Label(self, text="请用浏览器导出Netscape格式的cookie文件", foreground="gray")
        self.cookie_entry_tooltip.grid(row=8, column=1, sticky="w", padx=2)

        # 8. 操作按钮
        self.start_btn = tk.Button(self, text="开始下载", command=self.start_download, bg="#4CAF50", fg="white", activebackground="#388E3C", width=12)
        self.start_btn.grid(row=9, column=0, pady=15)
        self.pause_btn = tk.Button(self, text="暂停下载", state="disabled", bg="#FFA726", fg="white", activebackground="#F57C00", width=12)
        self.pause_btn.grid(row=9, column=1)
        self.cancel_btn = tk.Button(self, text="取消下载", state="disabled", bg="#E57373", fg="white", activebackground="#C62828", width=12)
        self.cancel_btn.grid(row=9, column=2)

        # 9. 状态/进度
        self.status_var = tk.StringVar(value="就绪")
        self.status_label = ttk.Label(self, textvariable=self.status_var, background="#F0F0F0", foreground="#0078D7", anchor="center", font=("微软雅黑", 12, "bold"))
        self.status_label.grid(row=10, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        self.progress_listbox = tk.Listbox(self, height=10, width=70, font=("Consolas", 10))
        self.progress_listbox.grid(row=11, column=0, columnspan=3, sticky="nsew", padx=10, pady=5)

        # 设置grid权重，使控件自适应拉伸
        for i in range(3):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(2, weight=1)   # url_text
        self.grid_rowconfigure(3, weight=0)   # playlist_frame
        self.grid_rowconfigure(11, weight=2)  # progress_listbox

        # 让playlist_frame内部自适应
        self.playlist_frame.grid_columnconfigure(0, weight=0)
        self.playlist_frame.grid_columnconfigure(1, weight=1)
        self.playlist_frame.grid_columnconfigure(2, weight=0)
        self.playlist_frame.grid_columnconfigure(3, weight=1)
        self.playlist_frame.grid_columnconfigure(4, weight=0)
        self.playlist_frame.grid_rowconfigure(1, weight=1)

        self.on_mode_change()
        self.on_proxy_toggle()

    def load_settings(self):
        self.path_var.set(self.config.get("download_path", ""))
        self.format_var.set(self.config.get("file_format", "mp4"))
        self.use_proxy_var.set(self.config.get("use_proxy", False))
        self.proxy_var.set(self.config.get("proxy_address", ""))
        self.cookie_var.set(self.config.get("cookie_file", ""))
        self.mode_var.set(self.config.get("mode", "single"))

    def save_settings(self):
        self.config["download_path"] = self.path_var.get()
        self.config["file_format"] = self.format_var.get()
        self.config["use_proxy"] = self.use_proxy_var.get()
        self.config["proxy_address"] = self.proxy_var.get()
        self.config["cookie_file"] = self.cookie_var.get()
        self.config["mode"] = self.mode_var.get()
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
        urls = [u.strip() for u in self.url_text.get("1.0", "end").strip().splitlines() if u.strip()]
        if not urls:
            messagebox.showerror("错误", "请至少输入一个有效链接。")
            return
        if not os.path.isdir(self.path_var.get()):
            messagebox.showerror("错误", "下载路径无效。")
            return
        self.save_settings()
        self.downloading = True
        self.status_var.set("正在下载...")
        self.progress_listbox.delete(0, "end")
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.cancel_btn.config(state="normal")
        playlist_range = None
        if self.mode_var.get() == "playlist":
            start = self.range_start.get().strip()
            end = self.range_end.get().strip()
            if start and end:
                playlist_range = f"{start}-{end}"
        # 修正：将下载路径传递给 yt-dlp 的 outtmpl
        config_copy = self.config.copy()
        download_path = self.path_var.get()
        # 确保路径末尾带分隔符
        if not download_path.endswith(os.sep):
            download_path += os.sep
        # 视频和音频输出模板
        if self.mode_var.get() == "playlist":
            outtmpl = os.path.join(download_path, "%(playlist_index)s-%(title)s.%(ext)s")
        else:
            outtmpl = os.path.join(download_path, "%(title)s.%(ext)s")
        config_copy["output_template"] = outtmpl

        def update_progress(percent, d):
            self.status_var.set(f"下载进度: {percent:.1f}%")
            # 只在Listbox中显示每个文件的最新进度（同一文件只保留一行）
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
                # 查找是否已存在该文件的进度行
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
        def run():
            try:
                download(urls, config_copy, make_progress_hook(update_progress), playlist_range)
                self.status_var.set("下载完成。")
            except Exception as e:
                self.status_var.set(f"错误: {e}")
            finally:
                self.downloading = False
                self.start_btn.config(state="normal")
                self.pause_btn.config(state="disabled")
                self.cancel_btn.config(state="disabled")
        self.download_thread = threading.Thread(target=run)
        self.download_thread.start()

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