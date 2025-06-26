import os

def collect_download_params(gui):
    params = {}
    params["urls"] = [u.strip() for u in gui.url_text.get("1.0", "end").strip().splitlines() if u.strip()]
    params["download_path"] = gui.path_var.get()
    params["file_format"] = gui.format_var.get()
    params["resolution"] = gui.resolution_var.get()
    params["bitrate"] = gui.bitrate_var.get()
    params["download_subtitle"] = gui.subtitle_var.get()
    params["download_cover"] = gui.cover_var.get()
    params["use_proxy"] = gui.use_proxy_var.get()
    params["proxy_address"] = gui.proxy_var.get()
    params["cookie_file"] = gui.cookie_var.get()
    params["mode"] = gui.mode_var.get()
    params["playlist_range"] = None
    if params["mode"] == "playlist":
        start = gui.range_start.get().strip()
        end = gui.range_end.get().strip()
        if start and end:
            params["playlist_range"] = f"{start}-{end}"
    return params

def validate_params(params):
    if not params["urls"]:
        return False, "请至少输入一个有效链接。"
    if not os.path.isdir(params["download_path"]):
        return False, "下载路径无效。"
    if not params["file_format"]:
        return False, "请选择文件格式。"
    # ...可扩展更多校验...
    return True, ""

def build_config_for_download(config, params):
    config_copy = config.copy()
    download_path = params["download_path"]
    if not download_path.endswith(os.sep):
        download_path += os.sep
    if params["mode"] == "playlist":
        outtmpl = os.path.join(download_path, "%(playlist_index)s-%(title)s.%(ext)s")
    else:
        outtmpl = os.path.join(download_path, "%(title)s.%(ext)s")
    config_copy["output_template"] = outtmpl
    config_copy["resolution"] = params["resolution"]
    config_copy["bitrate"] = params["bitrate"]
    config_copy["download_subtitle"] = params["download_subtitle"]
    config_copy["download_cover"] = params["download_cover"]
    config_copy["file_format"] = params["file_format"]
    config_copy["use_proxy"] = params["use_proxy"]
    config_copy["proxy_address"] = params["proxy_address"]
    config_copy["cookie_file"] = params["cookie_file"]
    config_copy["mode"] = params["mode"]
    return config_copy
