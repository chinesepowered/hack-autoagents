import base64
import logging

import httpx

from config import settings

logger = logging.getLogger(__name__)


async def analyze_video_frames(frames: list[str]) -> list[dict]:
    """Analyze video frames using Reka Vision API.

    Takes a list of frame file paths and returns visual insights for each.
    """
    if not settings.reka_api_key:
        logger.warning("REKA_API_KEY not set, using mock data")
        return _mock_visual_analysis(len(frames))

    results = []
    async with httpx.AsyncClient(timeout=60) as client:
        for i, frame_path in enumerate(frames):
            try:
                with open(frame_path, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")

                response = await client.post(
                    "https://api.reka.ai/v1/chat",
                    headers={
                        "Authorization": f"Bearer {settings.reka_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "reka-vision",
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image",
                                        "image": f"data:image/jpeg;base64,{image_data}",
                                    },
                                    {
                                        "type": "text",
                                        "text": (
                                            "Analyze this frame from a financial earnings call. "
                                            "Describe what you see: Is this a slide, chart, speaker view, "
                                            "or product demo? Extract any visible text, numbers, or data. "
                                            "If it's a chart, describe the trend. "
                                            "Respond in JSON format: "
                                            '{"content_type": "slide|chart|speaker|product_demo|other", '
                                            '"description": "...", "key_data": ["..."]}'
                                        ),
                                    },
                                ],
                            }
                        ],
                    },
                )
                response.raise_for_status()
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                results.append({
                    "timestamp": i * 30.0,  # 30-second intervals
                    "frame_path": frame_path,
                    "description": content,
                    "content_type": _classify_content(content),
                })

            except Exception as e:
                logger.error(f"Reka analysis failed for frame {i}: {e}")
                results.append({
                    "timestamp": i * 30.0,
                    "frame_path": frame_path,
                    "description": f"Analysis failed: {e}",
                    "content_type": "unknown",
                })

    return results


async def analyze_video_url(video_url: str) -> list[dict]:
    """Analyze a video directly via URL using Reka Vision API."""
    if not settings.reka_api_key:
        logger.warning("REKA_API_KEY not set, using mock data")
        return _mock_visual_analysis(5)

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                "https://api.reka.ai/v1/chat",
                headers={
                    "Authorization": f"Bearer {settings.reka_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "reka-vision",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "video_url", "video_url": video_url},
                                {
                                    "type": "text",
                                    "text": (
                                        "Analyze this earnings call video. For each distinct segment, describe: "
                                        "1) What is shown (slide, chart, speaker, etc.) "
                                        "2) Key data points visible "
                                        "3) Important visual changes "
                                        "Return a JSON array of segments with timestamp, content_type, "
                                        "description, and key_data fields."
                                    ),
                                },
                            ],
                        }
                    ],
                },
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return [{"timestamp": 0, "description": content, "content_type": "full_analysis"}]

    except Exception as e:
        logger.error(f"Reka video URL analysis failed: {e}")
        return [{"timestamp": 0, "description": str(e), "content_type": "error"}]


def _classify_content(description: str) -> str:
    desc_lower = description.lower()
    if "chart" in desc_lower or "graph" in desc_lower:
        return "chart"
    if "slide" in desc_lower or "presentation" in desc_lower:
        return "slide"
    if "speaker" in desc_lower or "person" in desc_lower:
        return "speaker"
    if "product" in desc_lower or "demo" in desc_lower:
        return "product_demo"
    return "other"


def _mock_visual_analysis(count: int) -> list[dict]:
    """Return mock data for development without API key."""
    mock_segments = [
        {
            "timestamp": 0.0,
            "description": "Title slide: 'Q4 2024 Earnings Call' with company logo and date",
            "content_type": "slide",
        },
        {
            "timestamp": 30.0,
            "description": "Revenue chart showing 23% YoY growth, from $89.5B to $110.2B",
            "content_type": "chart",
        },
        {
            "timestamp": 60.0,
            "description": "CEO speaking at podium, confident posture, gesturing at screen",
            "content_type": "speaker",
        },
        {
            "timestamp": 90.0,
            "description": "Product roadmap slide showing 3 new product launches planned for Q1 2025",
            "content_type": "slide",
        },
        {
            "timestamp": 120.0,
            "description": "Operating margin chart: improved from 29.8% to 33.1%, with Services segment highlighted",
            "content_type": "chart",
        },
    ]
    return mock_segments[:count]
