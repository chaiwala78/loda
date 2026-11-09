# MaQi Video Processing Bot

A GitHub Actions workflow that processes a video you own or have permission to use, adds a configurable MaQi watermark, and sends the result to Telegram.

## Setup

1. Add a video you own or are licensed to use under `input/` (for example, `input/video.mp4`).
2. In **Settings → Secrets and variables → Actions → Secrets**, add:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
3. Optionally add the repository Actions variable `WATERMARK_TEXT` (default: `MaQi`).
4. Open **Actions → Process and send video → Run workflow**.
5. Enter the repository path to the video, such as `input/video.mp4`.

The workflow uses FFmpeg to scale the video to a maximum width of 1280px, encode it as MP4, add a watermark, and send it to the configured Telegram chat.

## Notes

- Do not commit bot tokens, passwords, or session files.
- This starter workflow processes repository files only. It does not log into Instagram or download other creators' posts.
- Keep source videos within GitHub's repository size limits. For larger files, use an object-storage upload flow instead.
