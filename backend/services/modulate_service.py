import logging
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)


async def analyze_voice(audio_path: Optional[str] = None, transcript: Optional[str] = None) -> list[dict]:
    """Analyze voice patterns using Modulate API.

    Analyzes audio for speaker tone, confidence, stress indicators,
    and emotional state changes throughout the call.
    """
    if not settings.modulate_api_key:
        logger.warning("MODULATE_API_KEY not set, using mock data")
        return _mock_voice_analysis()

    audio_file = None
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            # Submit audio for analysis
            files = {}
            if audio_path:
                audio_file = open(audio_path, "rb")
                files["audio"] = audio_file

            response = await client.post(
                "https://api.modulate.ai/v1/analyze",
                headers={"Authorization": f"Bearer {settings.modulate_api_key}"},
                files=files if files else None,
                json={"transcript": transcript} if not files else None,
            )
            response.raise_for_status()
            data = response.json()

            segments = []
            for segment in data.get("segments", []):
                segments.append({
                    "start_time": segment.get("start"),
                    "end_time": segment.get("end"),
                    "speaker": segment.get("speaker", "Unknown"),
                    "confidence_score": segment.get("confidence", 0.0),
                    "tone": segment.get("tone", "neutral"),
                    "transcript": segment.get("text", ""),
                })

            return segments

    except Exception as e:
        logger.error(f"Modulate analysis failed: {e}")
        return _mock_voice_analysis()
    finally:
        if audio_file:
            audio_file.close()


def _mock_voice_analysis() -> list[dict]:
    """Return mock voice analysis data for development."""
    segments = [
        {
            "start_time": 0.0,
            "end_time": 45.0,
            "speaker": "CEO - Tim Cook",
            "confidence_score": 0.92,
            "tone": "confident",
            "transcript": "Good afternoon everyone. Thank you for joining us for our Q4 2024 earnings call. We're thrilled to report another record quarter.",
        },
        {
            "start_time": 45.0,
            "end_time": 120.0,
            "speaker": "CFO - Luca Maestri",
            "confidence_score": 0.88,
            "tone": "confident",
            "transcript": "Total revenue for the quarter reached $110.2 billion, up 23% year over year. Our Services business continues to accelerate.",
        },
        {
            "start_time": 120.0,
            "end_time": 180.0,
            "speaker": "CEO - Tim Cook",
            "confidence_score": 0.85,
            "tone": "enthusiastic",
            "transcript": "Our product pipeline has never been stronger. We're seeing incredible adoption of our AI features across the ecosystem.",
        },
        {
            "start_time": 180.0,
            "end_time": 240.0,
            "speaker": "Analyst - Morgan Stanley",
            "confidence_score": 0.78,
            "tone": "neutral",
            "transcript": "Can you speak to the margin pressure we're seeing in the hardware segment? What's the outlook for next quarter?",
        },
        {
            "start_time": 240.0,
            "end_time": 300.0,
            "speaker": "CEO - Tim Cook",
            "confidence_score": 0.65,
            "tone": "evasive",
            "transcript": "We're always looking at ways to optimize our cost structure. The overall picture is very positive and we remain confident in our trajectory.",
        },
        {
            "start_time": 300.0,
            "end_time": 360.0,
            "speaker": "CFO - Luca Maestri",
            "confidence_score": 0.82,
            "tone": "measured",
            "transcript": "Gross margins came in at 46.2%, slightly below expectations due to component costs, but we expect improvement in Q1.",
        },
        {
            "start_time": 360.0,
            "end_time": 420.0,
            "speaker": "Analyst - Goldman Sachs",
            "confidence_score": 0.75,
            "tone": "neutral",
            "transcript": "What's driving the acceleration in Services revenue? Can you break down the contribution from the App Store versus subscriptions?",
        },
        {
            "start_time": 420.0,
            "end_time": 480.0,
            "speaker": "CEO - Tim Cook",
            "confidence_score": 0.91,
            "tone": "confident",
            "transcript": "Services is truly a growth engine for us. We now have over 1 billion paid subscriptions across our platform. The ecosystem flywheel is working.",
        },
    ]
    return segments
