import logging
import os
import subprocess
import tempfile

logger = logging.getLogger(__name__)

TEMP_DIR = tempfile.mkdtemp(prefix="echomind_")


def download_media(url: str) -> dict:
    """Download video/audio from URL using yt-dlp. Returns paths to files."""
    output_template = os.path.join(TEMP_DIR, "%(id)s.%(ext)s")

    try:
        # Download video
        result = subprocess.run(
            [
                "yt-dlp",
                "--no-playlist",
                "-f", "best[height<=720]",
                "-o", output_template,
                "--write-info-json",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            logger.error(f"yt-dlp failed: {result.stderr}")
            return {"error": result.stderr}

        # Find the downloaded file
        video_file = None
        for f in os.listdir(TEMP_DIR):
            if f.endswith((".mp4", ".webm", ".mkv")):
                video_file = os.path.join(TEMP_DIR, f)
                break

        if not video_file:
            return {"error": "No video file found after download"}

        # Extract audio
        audio_file = video_file.rsplit(".", 1)[0] + ".wav"
        subprocess.run(
            [
                "ffmpeg", "-i", video_file,
                "-vn", "-acodec", "pcm_s16le",
                "-ar", "16000", "-ac", "1",
                audio_file, "-y",
            ],
            capture_output=True,
            timeout=120,
        )

        return {
            "video_path": video_file,
            "audio_path": audio_file if os.path.exists(audio_file) else None,
        }

    except subprocess.TimeoutExpired:
        return {"error": "Download timed out"}
    except Exception as e:
        return {"error": str(e)}


def extract_frames(video_path: str, interval_seconds: int = 30) -> list[str]:
    """Extract frames from video at regular intervals."""
    frames_dir = os.path.join(TEMP_DIR, "frames")
    os.makedirs(frames_dir, exist_ok=True)

    try:
        subprocess.run(
            [
                "ffmpeg", "-i", video_path,
                "-vf", f"fps=1/{interval_seconds}",
                os.path.join(frames_dir, "frame_%04d.jpg"),
                "-y",
            ],
            capture_output=True,
            timeout=120,
        )

        frames = sorted(
            os.path.join(frames_dir, f)
            for f in os.listdir(frames_dir)
            if f.endswith(".jpg")
        )
        return frames

    except Exception as e:
        logger.error(f"Frame extraction failed: {e}")
        return []
