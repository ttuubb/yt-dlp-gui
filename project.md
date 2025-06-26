YouTube Downloader Design Scheme
Overview
Design a Python-based GUI application for downloading YouTube videos/audios, supporting both single video (non-playlist) and playlist modes using yt-dlp. The application allows batch URL input, download path selection, format selection, proxy settings, cookie file support for authenticated downloads, and persistent configuration storage.
Functional Requirements
Core Features

URL Input:
Support single or multiple YouTube video/playlist URLs (one per line).
Modes: Single video/audio, Playlist.


Download Path:
Select folder for saving files, default to system Downloads directory.


File Format:
Options: mp4 (video), mp3 (audio), m4a (audio), webm (video).


Proxy Settings:
Enable/disable proxy, input address (e.g., http://127.0.0.1:10808).


Cookie File Support:
Allow users to specify a cookie file path (e.g., exported from browser in Netscape format).
Support downloading restricted/private videos requiring authentication.


Settings Persistence:
Save download path, format, proxy settings, and cookie file path; load on startup.


Progress Display:
Show progress for single video or each playlist item.


Error Handling:
Validate URLs, paths, cookie file; handle download failures.



Playlist-Specific Features

Mode Selection:
Choose between single video and playlist modes.


Playlist Options:
Specify range (e.g., videos 1-5).
Display playlist info (title, video count).


Batch Control:
Pause/cancel playlist downloads.



Technical Stack

GUI: tkinter (cross-platform, Python built-in).
Download Core: yt-dlp (supports single video, playlist, and cookie authentication).
Config: JSON file (~/.yt_downloader_config.json).
Dependencies: Python 3.x, yt-dlp (pip install yt-dlp), FFmpeg (for audio extraction).

Interface Design
Layout

Window: 600x650 pixels, grid layout.
Components:
Mode Selection:
Label: Download Mode:
Radio buttons: "Single Video/Audio", "Playlist".


URL Input:
Label:/YouTube URL (one per line):
Text box: 5 rows, 50 chars.


Playlist Options (enabled in playlist mode):
Label: Playlist Range:
Two Entry fields for start/end video index (optional, empty for full playlist).
Button: "Get Playlist Info" (shows title, video count).


Download Path:
Label: Download Path:
Entry + Browse button.


File Format:
Label: File Format:
Combobox: mp4, mp3, m4a, webm.


Proxy Settings:
Checkbutton: Use Proxy.
Label: Proxy Address (e.g., http://127.0.0.1:10808):
Entry (enabled/disabled based on Checkbutton).


Cookie File:
Label: Cookie File Path:
Entry + Browse button (for selecting cookie file, e.g., cookies.txt).


Actions:
Buttons: Start Download, Pause Download, Cancel Download.


Status Display:
Label: Overall progress (e.g., "Downloading: 50%").
Listbox: Per-video progress for playlists (e.g., "Video 1/10: 50%").





Dynamic Behavior

Enable/disable playlist options based on mode selection.
Enable/disable proxy and cookie input fields based on respective Checkbutton states.
Display playlist metadata on "Get Playlist Info" click.
Update Pause/Cancel button states during download.
Show tooltips for cookie file input (e.g., "Export cookies from browser in Netscape format").

System Architecture
Modules

GUI Module:
Manages interface creation, event handling, and dynamic updates.
Handles mode switching, playlist info display, and cookie file selection.


Download Module:
Uses yt-dlp for single video/playlist downloads.
Configures parameters for formats, proxy, and cookies.


Config Module:
Saves/loads settings (path, format, proxy, cookie file path, mode) in JSON.


Progress Module:
Captures yt-dlp progress callbacks, updates single or playlist progress.


Playlist Info Module:
Fetches playlist metadata (title, video count) using yt-dlp.



Data Flow

User selects mode (single video/playlist).
Inputs URLs; for playlist mode, optionally checks playlist info and sets range.
Configures path, format, proxy, and cookie file.
On "Start Download":
Validates inputs (URLs, path, cookie file existence).
Saves settings to JSON.
Configures yt-dlp parameters based on mode, format, proxy, and cookies.
Executes download, updates progress.


Displays completion or error messages.

Implementation Details
Download Modes

Single Video/Audio:
Video: bestvideo[ext=format]+bestaudio/best.
Audio: bestaudio/best + FFmpeg post-processing (mp3: preferredcodec=mp3, preferredquality=192; m4a: preferredcodec=m4a).
Output: %(title)s.%(ext)s.


Playlist:
Use playlist_items for range (e.g., 1-5).
Output: %(playlist_index)s-%(title)s.%(ext)s.
Fetch metadata with extract_info(download=False).



Cookie Support

Use yt-dlp's --cookies parameter to pass cookie file path.
Validate cookie file existence and format (Netscape format, e.g., cookies.txt from browser).
Support authentication for restricted/private videos.

Settings

Save: Download path, format, proxy (enable/address), cookie file path, mode.
File: ~/.yt_downloader_config.json.
Load: Populate GUI fields on startup.

Progress & Control

Progress:
Single mode: Display percentage in Label.
Playlist mode: Show per-video progress in Listbox (e.g., "Video 1/10: 50%").


Pause/Cancel:
Pause: Use yt-dlp pause mechanism or thread control.
Cancel: Terminate yt-dlp process, clean temporary files.



Error Handling

Input Validation:
Check URLs (valid YouTube format).
Verify download path (exists, writable).
Validate cookie file (exists, readable, correct format).
Check playlist range (valid numbers, within bounds).


Download Errors:
Catch yt-dlp exceptions (e.g., network issues, invalid cookies).
Display user-friendly error messages (e.g., "Invalid cookie file, please export from browser").



Development Workflow

Environment Setup:
Install Python 3.x, yt-dlp, FFmpeg.
Test yt-dlp with cookies for restricted videos.


GUI Development:
Create tkinter interface with mode selection, cookie input, and playlist controls.
Implement dynamic enabling/disabling of fields.


Download Logic:
Integrate yt-dlp for single video and playlist downloads.
Add cookie file support via --cookies parameter.


Config & Progress:
Implement JSON save/load for settings.
Add progress callbacks and pause/cancel functionality.


Testing:
Test single video downloads (all formats, with/without cookies).
Test playlist downloads (full list, specific range).
Test proxy and cookie functionality, error cases (invalid URLs, cookies).


Optimization:
Improve GUI responsiveness with asynchronous progress updates.
Enhance error messages for clarity.



Extensibility

Additional Formats: Support flac, wav, etc.
Advanced Options:
Resolution selection (e.g., 720p, 1080p).
Subtitle downloads.
Playlist video selection via checkboxes.


Multi-threading: Parallel downloads for playlist items.
Batch Import: Support URL lists from txt/csv files.

User Experience

Prompts: Mode-specific hints near URL input (e.g., "Enter playlist URL for Playlist mode").
Playlist Preview: Show video titles/thumbnails (via yt-dlp metadata).
Cookie Guidance: Tooltip explaining how to export cookies (e.g., "Use browser extension to export cookies in Netscape format").
Progress Visualization: Add progress bars for single and playlist downloads.

Risks & Solutions

Cookie File Issues:
Risk: Invalid or expired cookies.
Solution: Validate file format, prompt user to re-export cookies.


Playlist URL Failure:
Risk: Invalid or private playlists.
Solution: Validate URLs, use cookies for access, show error messages.


Large Playlist Downloads:
Risk: Long download times.
Solution: Support pause/resume, multi-threading.


yt-dlp Updates:
Risk: Parameter changes.
Solution: Test with latest yt-dlp, prompt user updates.



Deployment & Usage

Requirements: Python, yt-dlp, FFmpeg.
Packaging: Use PyInstaller for executable.
Usage:
Select mode (single video/playlist).
Input URLs; for playlists, check info and set range.
Configure path, format, proxy, and cookie file.
Start download, monitor progress, pause/cancel if needed.
Receive completion/error notifications.

## 版本控制与仓库地址
rm -rf .git
本项目已托管于 GitHub，仓库地址如下：

[https://github.com/ttuubb/YT-cline.git](https://github.com/ttuubb/YT-cline.git)

请使用 `git clone` 命令拉取代码，或直接在 GitHub 上查看、提交 issue 与协作开发。