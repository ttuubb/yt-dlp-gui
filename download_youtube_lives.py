import subprocess
import os
import json
from datetime import datetime, timedelta

# YouTube 频道列表
channels = [
    "https://www.youtube.com/@dakang",
    "https://www.youtube.com/@wongkim728",
    "https://www.youtube.com/@Laozivip-up"
]

# 代理设置
proxy = "127.0.0.1:10808"

# 计算三天前的日期
three_days_ago = datetime.now() - timedelta(days=3)
date_after = three_days_ago.strftime("%Y%m%d")

print(f"Downloading live videos updated after: {date_after}")

for channel_url in channels:
    print(f"\nProcessing channel: {channel_url}")
    
    # yt-dlp 命令：首先获取所有直播视频的元数据
    # --dump-json: 输出JSON格式的元数据
    # --flat-playlist: 避免下载整个播放列表，只获取视频信息
    # --match-filter "is_live": 仅获取直播视频信息
    info_command = [
        "yt-dlp",
        "--proxy", proxy,
        "--match-filter", "is_live",
        "--dump-json",
        "--flat-playlist",
        channel_url
    ]

    print(f"Fetching live video info for {channel_url}: {' '.join(info_command)}")
    try:
        process = subprocess.run(info_command, capture_output=True, text=True, check=True, encoding='utf-8')
        videos_info = process.stdout.strip().split('\n')
        
        downloaded_count = 0
        for video_json in videos_info:
            try:
                video_data = json.loads(video_json)
                upload_date_str = video_data.get('upload_date')
                
                if upload_date_str:
                    # yt-dlp的upload_date格式是YYYYMMDD
                    upload_datetime = datetime.strptime(upload_date_str, "%Y%m%d")
                    
                    if upload_datetime >= three_days_ago:
                        video_url = video_data.get('webpage_url')
                        if video_url:
                            # 构建输出模板，使用视频自己的upload_date作为文件夹名
                            # %(upload_date)s 是 yt-dlp 提供的视频上传日期
                            output_template = os.path.join(upload_date_str, "%(title)s.%(ext)s")

                            download_command = [
                                "yt-dlp",
                                "--proxy", proxy,
                                "--extract-audio",
                                "--audio-format", "mp3",
                                "-o", output_template,
                                video_url
                            ]
                            print(f"\nDownloading audio for '{video_data.get('title')}' ({video_url})")
                            print(f"Command: {' '.join(download_command)}")
                            subprocess.run(download_command, check=True)
                            print(f"Successfully downloaded audio for '{video_data.get('title')}'")
                            downloaded_count += 1
                        else:
                            print(f"Warning: Could not find URL for video '{video_data.get('title')}'")
                    else:
                        print(f"Skipping '{video_data.get('title')}' (uploaded on {upload_date_str}, older than 3 days)")
                else:
                    print(f"Warning: Could not find upload date for video '{video_data.get('title')}'")

            except json.JSONDecodeError:
                print(f"Error decoding JSON for video info: {video_json}")
            except subprocess.CalledProcessError as e:
                print(f"Error downloading audio for a video: {e}")
        
        if downloaded_count == 0:
            print(f"No live videos updated in the last 3 days found for {channel_url}.")
        else:
            print(f"Finished processing {channel_url}. Downloaded {downloaded_count} audio files.")

    except subprocess.CalledProcessError as e:
        print(f"Error fetching info for {channel_url}: {e}")
    except FileNotFoundError:
        print("Error: yt-dlp command not found. Please ensure yt-dlp is installed and in your PATH.")

print("\nScript finished.")
