import os
import subprocess
from datetime import datetime, timedelta

# 频道链接列表
channels = [
    "https://www.youtube.com/@dakang",
    "https://www.youtube.com/@wongkim728",
    "https://www.youtube.com/@Laozivip-up"
]

# 本地代理配置
proxy = "127.0.0.1:10808"

# 获取三天前的时间
now = datetime.utcnow()
three_days_ago = now - timedelta(days=3)

def get_video_list(channel_url):
    """获取频道视频信息列表（json）"""
    cmd = [
        "yt-dlp",
        "--proxy", f"http://{proxy}",
        "--dateafter", three_days_ago.strftime("%Y%m%d"),
        "--match-filter", "is_live",
        "--flat-playlist",
        "-j",
        channel_url
    ]
    print(f"获取：{channel_url}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    videos = []
    for line in result.stdout.strip().split("\n"):
        try:
            import json
            video_info = json.loads(line)
            videos.append(video_info)
        except Exception as e:
            print("解析出错：", e)
    return videos

def download_video(video_url, upload_date):
    """下载单个视频到指定日期目录"""
    folder_name = upload_date
    os.makedirs(folder_name, exist_ok=True)
    output_template = os.path.join(folder_name, "%(title)s [%(id)s].%(ext)s")
    cmd = [
        "yt-dlp",
        "--proxy", f"http://{proxy}",
        "-f", "best",
        "-o", output_template,
        video_url
    ]
    subprocess.run(cmd)

def main():
    for channel in channels:
        videos = get_video_list(channel)
        for video in videos:
            video_url = f"https://www.youtube.com/watch?v={video['id']}"
            upload_date = video.get("upload_date", None)
            if not upload_date:
                continue
            # 下载
            print(f"准备下载: {video_url} => 日期目录: {upload_date}")
            download_video(video_url, upload_date)

if __name__ == "__main__":
    main()
