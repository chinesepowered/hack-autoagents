import logging
import os
import shutil
import subprocess
import tempfile

logger = logging.getLogger(__name__)


def download_media(url: str) -> dict:
    """Download video/audio from URL using yt-dlp. Returns paths to files."""
    work_dir = tempfile.mkdtemp(prefix="echomind_")
    output_template = os.path.join(work_dir, "%(id)s.%(ext)s")

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
            shutil.rmtree(work_dir, ignore_errors=True)
            return {"error": result.stderr}

        # Find the downloaded file
        video_file = None
        for f in os.listdir(work_dir):
            if f.endswith((".mp4", ".webm", ".mkv")):
                video_file = os.path.join(work_dir, f)
                break

        if not video_file:
            shutil.rmtree(work_dir, ignore_errors=True)
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
            "work_dir": work_dir,
        }

    except subprocess.TimeoutExpired:
        shutil.rmtree(work_dir, ignore_errors=True)
        return {"error": "Download timed out"}
    except Exception as e:
        shutil.rmtree(work_dir, ignore_errors=True)
        return {"error": str(e)}


def extract_frames(video_path: str, interval_seconds: int = 30) -> list[str]:
    """Extract frames from video at regular intervals."""
    frames_dir = os.path.join(os.path.dirname(video_path), "frames")
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


def cleanup_work_dir(work_dir: str):
    """Clean up temporary files after processing."""
    if work_dir and os.path.isdir(work_dir):
        shutil.rmtree(work_dir, ignore_errors=True)
