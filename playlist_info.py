import yt_dlp

def get_playlist_info(url, config):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "skip_download": True,
    }
    if config.get("use_proxy"):
        ydl_opts["proxy"] = config.get("proxy_address", "")
    if config.get("cookie_file"):
        ydl_opts["cookiefile"] = config.get("cookie_file")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "count": len(info.get("entries", []))
        }
