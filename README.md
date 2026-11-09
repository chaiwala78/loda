# MaQi Video Processing Bot

GitHub Actions workflow to process a video you own or have permission to use, apply a MaQi-style branded overlay, and send it to your Telegram bot.

## Current setup

1. Put a permitted source video in the repository, for example `input/video.mp4`.
2. Fill `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `config.py`. Keep this repository private while using this temporary testing configuration.
3. Open **Actions → Process and send video → Run workflow**.
4. Enter `input/video.mp4` as the video path.

The workflow uses FFmpeg to scale the video to a maximum width of 1280px, add a top **WATCH & DOWNLOAD ON MAQI** banner, a bottom **LINK IN BIO** banner, and a MaQi corner watermark, then encode and send an MP4 to Telegram.

A SHA-256 fingerprint is saved in `.processed_videos.txt` after successful upload. Re-running the workflow with the same source file skips the duplicate.

## Configuration

Change overlay text in `config.py`. Environment variables override config values, so the project can later move to GitHub Actions Secrets without changing the processing code.

## Current limitation

This version processes repository video files. It does not fetch videos from Instagram accounts. The source must be a video you own or have permission to use.
