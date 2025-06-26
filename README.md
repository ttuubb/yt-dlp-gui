# YouTube 视频下载器

本项目是一个基于 Python 和 tkinter 的 YouTube 视频/音频批量下载工具，支持单视频和播放列表下载，支持代理、Cookie、格式选择、断点续传等功能。

## 功能特性

- 支持批量输入 YouTube 视频或播放列表链接
- 支持单视频/音频和播放列表下载模式
- 支持 mp4、mp3、m4a、webm 格式选择
- 支持代理设置（如科学上网）
- 支持 Cookie 文件（可下载会员/私有视频）
- 支持下载路径自定义
- 下载进度实时显示，支持多任务
- 配置自动保存和加载

## 依赖环境

- Python 3.7 及以上
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) (`pip install yt-dlp`)
- [FFmpeg](https://ffmpeg.org/)（用于音频提取，需自行安装）
- tkinter（Python 标准库自带）

## 安装与运行

1. 克隆仓库

   ```bash
   git clone https://github.com/ttuubb/YT-cline.git
   cd YT-cline
   ```

2. 安装依赖

   ```bash
   pip install yt-dlp
   # 确保已安装 FFmpeg，并配置到系统环境变量
   ```

3. 运行程序

   ```bash
   python /home/ttuubb/Document/yt-dlp/gui.py
   ```

## 配置说明

- 程序会自动在用户主目录下生成 `~/.yt_downloader_config.json` 用于保存下载路径、格式、代理、Cookie 等设置。
- Cookie 文件请用浏览器插件导出为 Netscape 格式（如 `cookies.txt`）。

## 常见问题

- **下载速度慢/失败？**  
  请检查网络环境，或配置代理。
- **无法下载会员/私有视频？**  
  请正确导入浏览器 Cookie 文件。
- **音频提取失败？**  
  请确保 FFmpeg 已正确安装并加入环境变量。

## 开源协议

本项目采用 MIT 协议，欢迎自由使用和二次开发。

## 仓库地址

[https://github.com/ttuubb/YT-cline.git](https://github.com/ttuubb/YT-cline.git)

## Ubuntu 下打包为可执行文件

你可以使用 PyInstaller 工具将本项目打包为 Ubuntu 下的可执行文件，步骤如下：

1. **安装依赖**

   ```bash
   sudo apt update
   sudo apt install python3 python3-pip ffmpeg
   pip3 install pyinstaller yt-dlp
   ```

2. **进入项目目录**

   ```bash
   cd /home/ttuubb/Document/yt-dlp
   ```

3. **打包命令**

   ```bash
   pyinstaller --onefile --noconsole gui.py
   ```

   - `--onefile` 生成单一可执行文件，`--noconsole` 不弹出终端窗口（如需调试可去掉）。
   - 打包完成后，`dist/gui` 即为可执行文件。

4. **运行打包后的程序**

   ```bash
   ./dist/gui
   ```

5. **注意事项**
   - 打包后首次运行可能较慢。
   - 若需图标，需将 `icon.ico` 转为 `.png` 并用 `--icon=icon.png` 参数。
   - 若遇到字体、tkinter、ffmpeg等依赖问题，请确保系统已安装相关包。

---

如需自动化脚本或遇到打包问题，可随时提问。
