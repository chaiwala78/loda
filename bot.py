import hashlib
import os
import subprocess
import sys
from pathlib import Path

import requests

# config.py is kept in the private repository for quick testing.
# Environment variables (GitHub Secrets) override config.py automatically.
try:
    import config
except ImportError:
    config = None


def setting(name: str, default: str = "") -> str:
    value = os.environ.get(name)
    if value:
        return value
    return str(getattr(config, name, default)) if config else default


TOKEN = setting("TELEGRAM_BOT_TOKEN")
CHAT_ID = setting("TELEGRAM_CHAT_ID")
VIDEO = Path(os.environ.get("VIDEO_PATH", ""))
TOP_TEXT = setting("TOP_TEXT", "WATCH & DOWNLOAD ON MAQI")
BOTTOM_TEXT = setting("BOTTOM_TEXT", "LINK IN BIO")
WATERMARK = setting("WATERMARK_TEXT", "MaQi")
PROCESSED_FILE = Path(".processed_videos.txt")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def ffmpeg_escape(value: str) -> str:
    return (value.replace("\\", r"\\")
                 .replace(":", r"\:")
                 .replace("'", r"\'")
                 .replace("%", r"\%")
                 .replace(",", r"\,"))


def main() -> None:
    if not TOKEN or not CHAT_ID:
        fail("Fill TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in config.py.")
    if not VIDEO.is_file():
        fail(f"Video not found: {VIDEO}. Add a video you own or have permission to use.")

    digest = hashlib.sha256(VIDEO.read_bytes()).hexdigest()
    previous = PROCESSED_FILE.read_text().splitlines() if PROCESSED_FILE.exists() else []
    if digest in previous:
        print("Already processed and sent. Skipping duplicate.")
        return

    output = Path("/tmp/maqi_processed.mp4")
    top = ffmpeg_escape(TOP_TEXT)
    bottom = ffmpeg_escape(BOTTOM_TEXT)
    mark = ffmpeg_escape(WATERMARK)

    # Clean branded layout: top banner, bottom CTA, and a small corner mark.
    vf = (
        "scale='min(1280,iw)':-2,"
        "drawbox=x=0:y=0:w=iw:h=ih*0.105:color=black@0.62:t=fill,"
        f"drawtext=text='{top}':fontcolor=white:fontsize=30:"
        "borderw=2:bordercolor=black@0.75:x=(w-text_w)/2:y=ih*0.025,"
        "drawbox=x=0:y=ih*0.88:w=iw:h=ih*0.12:color=black@0.62:t=fill,"
        f"drawtext=text='{bottom}':fontcolor=white:fontsize=34:"
        "borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=ih*0.905,"
        f"drawtext=text='{mark}':fontcolor=white:fontsize=22:"
        "borderw=2:bordercolor=black@0.8:x=w-text_w-18:y=h-th-ih*0.135"
    )

    subprocess.run(
        ["ffmpeg", "-y", "-i", str(VIDEO), "-vf", vf,
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
         str(output)],
        check=True,
    )

    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
    with output.open("rb") as video_file:
        response = requests.post(
            url,
            data={"chat_id": CHAT_ID, "supports_streaming": "true"},
            files={"video": (output.name, video_file, "video/mp4")},
            timeout=300,
        )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        fail(f"Telegram API returned an error: {payload}")

    with PROCESSED_FILE.open("a", encoding="utf-8") as state:
        state.write(digest + "\\n")
    print("Processed video sent to Telegram; duplicate hash recorded.")


if __name__ == "__main__":
    main()
