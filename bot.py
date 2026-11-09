import os
import subprocess
import sys
from pathlib import Path

import requests

VIDEO = Path(os.environ.get("VIDEO_PATH", ""))
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
WATERMARK = os.environ.get("WATERMARK_TEXT", "MaQi")

def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)

def main() -> None:
    if not TOKEN or not CHAT_ID:
        fail("Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in GitHub Actions secrets.")
    if not VIDEO.is_file():
        fail(f"Video not found: {VIDEO}. Add your own/licensed video to the repository first.")

    output = Path("/tmp/maqi_processed.mp4")
    escaped = WATERMARK.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    vf = (
        "scale='min(1280,iw)':-2,"
        "drawtext=text='" + escaped + "':"
        "fontcolor=white:fontsize=28:"
        "borderw=2:bordercolor=black@0.8:"
        "x=w-tw-24:y=h-th-24"
    )

    subprocess.run(
        ["ffmpeg", "-y", "-i", str(VIDEO), "-vf", vf,
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
         str(output)],
        check=True,
    )

    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
    with output.open("rb") as file:
        response = requests.post(
            url,
            data={"chat_id": CHAT_ID, "supports_streaming": "true"},
            files={"video": (output.name, file, "video/mp4")},
            timeout=300,
        )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        fail(f"Telegram API returned an error: {payload}")
    print("Video processed and sent to Telegram.")

if __name__ == "__main__":
    main()
