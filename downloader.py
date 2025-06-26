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
    if fmt in ("mp3", "m4a"):
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": fmt,
            "preferredquality": "192"
        }]
    elif fmt in ("mp4", "webm"):
        ydl_opts["format"] = f"bestvideo[ext={fmt}]+bestaudio/best" if fmt != "webm" else "bestvideo[ext=webm]+bestaudio/best"
        ydl_opts["merge_output_format"] = fmt

    if config.get("use_proxy"):
        ydl_opts["proxy"] = config.get("proxy_address", "")

    if config.get("cookie_file"):
        ydl_opts["cookiefile"] = config.get("cookie_file")

    if playlist_range:
        ydl_opts["playlist_items"] = playlist_range

    return ydl_opts

def download(urls, config, progress_hook, playlist_range=None):
    ydl_opts = build_ydl_opts(config, progress_hook, playlist_range)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)
