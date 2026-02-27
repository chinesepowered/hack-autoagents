"""EchoMind Cron Job — Monitors for new earnings calls and triggers analysis.

Runs on a schedule via Render Cron Job service. Uses Yutori Scouting API
to check for newly published earnings calls and submits them for analysis.
"""

import json
import logging
import os

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_api_host = os.getenv("ECHOMIND_API_URL", "http://localhost:8000")
# Render's fromService host property gives a bare hostname without protocol
ECHOMIND_API_URL = _api_host if _api_host.startswith("http") else f"https://{_api_host}"
YUTORI_API_KEY = os.getenv("YUTORI_API_KEY", "")

# Companies to monitor
WATCHLIST = [
    "Apple AAPL earnings call",
    "Microsoft MSFT earnings call",
    "Google GOOG earnings call",
    "Amazon AMZN earnings call",
    "Tesla TSLA earnings call",
    "NVIDIA NVDA earnings call",
    "Meta META earnings call",
]


def check_for_new_earnings_calls():
    """Check for newly published earnings calls using Yutori."""
    if not YUTORI_API_KEY:
        logger.info("YUTORI_API_KEY not set — running in demo mode")
        logger.info("Would check for new earnings calls from watchlist:")
        for company in WATCHLIST:
            logger.info(f"  - {company}")
        return

    with httpx.Client(timeout=60) as client:
        for query in WATCHLIST:
            try:
                response = client.post(
                    "https://api.yutori.com/v1/research",
                    headers={
                        "Authorization": f"Bearer {YUTORI_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "query": f"Latest {query} video recording published in the last 24 hours",
                        "instructions": (
                            "Find the most recent earnings call video URL. "
                            "Return only if published in the last 24 hours. "
                            "Include the direct video URL if available."
                        ),
                    },
                )
                response.raise_for_status()
                result = response.json()

                video_url = result.get("video_url")
                if video_url:
                    logger.info(f"New earnings call found: {query} -> {video_url}")
                    _submit_for_analysis(client, video_url)

            except Exception as e:
                logger.error(f"Failed to check {query}: {e}")


def _submit_for_analysis(client: httpx.Client, video_url: str):
    """Submit a new earnings call URL to the EchoMind API for analysis."""
    try:
        response = client.post(
            f"{ECHOMIND_API_URL}/api/analyze",
            json={"url": video_url},
        )
        response.raise_for_status()
        data = response.json()
        logger.info(f"Analysis submitted: {data.get('analysis_id')}")
    except Exception as e:
        logger.error(f"Failed to submit analysis: {e}")


if __name__ == "__main__":
    logger.info("EchoMind Cron: Checking for new earnings calls...")
    check_for_new_earnings_calls()
    logger.info("EchoMind Cron: Done.")
