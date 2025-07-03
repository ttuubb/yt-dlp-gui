import subprocess
from datetime import datetime, timedelta
import csv
def get_list():
    channels = [
        "https://www.youtube.com/@dakang",
        "https://www.youtube.com/@wongkim728",
        "https://www.youtube.com/@Laozivip-up"
    ]

    date_after = (datetime.now() - timedelta(days=3)).strftime('%Y%m%d')
    infos = []

    for channel in channels:
        streams_url = channel.rstrip('/') + '/streams'
        cmd = [
            "yt-dlp",
            streams_url,
            "--dateafter", date_after,
            "--flat-playlist",
            "--print", "%(webpage_url)s\t%(title)s\t%(upload_date)s",
            "--cookies", "cookies.txt"
        ]
        print(f"正在提取频道: {streams_url}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        lines = result.stdout.strip().splitlines()
        for line in lines:
            parts = line.split('\t')
            if len(parts) == 3:
                url, title, upload_date = parts
                infos.append([url, title, upload_date])

    with open("live_video_infos.csv", "w", encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["url", "title", "upload_date"])
        writer.writerows(infos)
if '__name__' == '__main__':
    get_list()