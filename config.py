import os
import json

CONFIG_PATH = os.path.expanduser("~/.yt_downloader_config.json")

DEFAULT_CONFIG = {
    "download_path": os.path.expanduser("~/Downloads"),
    "file_format": "mp4",
    "use_proxy": False,
    "proxy_address": "",
    "cookie_file": "",
    "mode": "single"
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return {**DEFAULT_CONFIG, **config}
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass