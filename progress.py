def make_progress_hook(update_func):
    def hook(d):
        if d["status"] == "downloading":
            percent = d.get("downloaded_bytes", 0) / max(d.get("total_bytes", 1), 1) * 100 if d.get("total_bytes") else 0
            update_func(percent, d)
        elif d["status"] == "finished":
            update_func(100, d)
    return hook
