import yt_dlp

def build_ydl_opts(config, progress_hook, playlist_range=None):
    ydl_opts = {
        "outtmpl": config.get("output_template", "%(title)s.%(ext)s"),
        "progress_hooks": [progress_hook],
        "format": "bestvideo+bestaudio/best",
        "noplaylist": config.get("mode") == "single",
        "quiet": True,
        "ignoreerrors": True,
        "merge_output_format": config.get("file_format", "mp4"),
    }
    fmt = config.get("file_format", "mp4")
    if fmt in ("mp3", "m4a", "flac", "wav", "aac", "opus"):
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": fmt,
            "preferredquality": "192"
        }]
    elif fmt in ("mp4", "webm", "mov", "avi"):
        ydl_opts["format"] = f"bestvideo[ext={fmt}]+bestaudio/best" if fmt != "webm" else "bestvideo[ext=webm]+bestaudio/best"
        ydl_opts["merge_output_format"] = fmt

    # 分辨率
    resolution = config.get("resolution")
    if resolution and resolution not in ("最高", "音频"):
        ydl_opts["format"] = f"bestvideo[height={resolution.replace('p','')}]+bestaudio/best/best[height={resolution.replace('p','')}]"

    # 码率
    bitrate = config.get("bitrate")
    if bitrate and bitrate != "默认":
        if "postprocessors" not in ydl_opts:
            ydl_opts["postprocessors"] = []
        for pp in ydl_opts["postprocessors"]:
            if pp.get("key") == "FFmpegExtractAudio":
                pp["preferredquality"] = bitrate.replace("k", "")

    # 字幕
    if config.get("download_subtitle"):
        ydl_opts["writesubtitles"] = True
        ydl_opts["subtitleslangs"] = ["all"]

    # 封面
    if config.get("download_cover"):
        ydl_opts["embedthumbnail"] = True
        if "postprocessors" not in ydl_opts:
            ydl_opts["postprocessors"] = []
        ydl_opts["postprocessors"].append({"key": "EmbedThumbnail"})

    if config.get("use_proxy"):
        ydl_opts["proxy"] = config.get("proxy_address", "")

    if config.get("cookie_file"):
        ydl_opts["cookiefile"] = config.get("cookie_file")

    if playlist_range:
        ydl_opts["playlist_items"] = playlist_range

    return ydl_opts

def download(urls, config, progress_hook, playlist_range=None, stop_event=None, pause_event=None):
    # 包装进度回调，支持暂停/取消
    def wrapped_hook(d):
        if stop_event and stop_event.is_set():
            raise Exception("用户取消下载")
        if pause_event:
            while pause_event.is_set():
                import time; time.sleep(0.2)
        progress_hook(d)
    ydl_opts = build_ydl_opts(config, wrapped_hook, playlist_range)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)
