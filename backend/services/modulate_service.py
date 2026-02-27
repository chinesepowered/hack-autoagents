import logging
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)

MODULATE_API_URL = "https://modulate-developer-apis.com/api/velma-2-stt-batch"


async def analyze_voice(audio_path: Optional[str] = None, transcript: Optional[str] = None) -> list[dict]:
    """Analyze voice patterns using Modulate Velma-2 API.

    Analyzes audio for speaker diarization, emotion detection,
    and accent identification.
    """
    if not settings.modulate_api_key:
        logger.warning("MODULATE_API_KEY not set, using mock data")
        return _mock_voice_analysis()

    if not audio_path:
        logger.warning("No audio path provided, using mock data")
        return _mock_voice_analysis()

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            with open(audio_path, "rb") as audio_file:
                response = await client.post(
                    MODULATE_API_URL,
                    headers={"X-API-Key": settings.modulate_api_key},
                    files={"upload_file": audio_file},
                    data={
                        "speaker_diarization": "true",
                        "emotion_signal": "true",
                    },
                )
                response.raise_for_status()
                data = response.json()

            segments = []
            for utterance in data.get("utterances", []):
                segments.append({
                    "start_time": utterance.get("start_ms", 0) / 1000.0,
                    "end_time": (utterance.get("start_ms", 0) + utterance.get("duration_ms", 0)) / 1000.0,
                    "speaker": f"Speaker {utterance.get('speaker', 'Unknown')}",
                    "confidence_score": _emotion_to_confidence(utterance.get("emotion", "Neutral")),
                    "tone": utterance.get("emotion", "neutral").lower(),
                    "transcript": utterance.get("text", ""),
                    "accent": utterance.get("accent"),
                    "language": utterance.get("language"),
                })

            return segments if segments else _mock_voice_analysis()

    except Exception as e:
        logger.error(f"Modulate analysis failed: {e}")
        return _mock_voice_analysis()


def _emotion_to_confidence(emotion: str) -> float:
    """Map emotion to a confidence score (for demo purposes)."""
    emotion_scores = {
        "Neutral": 0.75,
        "Happy": 0.90,
        "Confident": 0.92,
        "Excited": 0.88,
        "Sad": 0.60,
        "Angry": 0.55,
        "Fear": 0.50,
        "Surprised": 0.70,
    }
    return emotion_scores.get(emotion, 0.75)


def _mock_voice_analysis() -> list[dict]:
    """Return mock voice analysis data for development."""
    segments = [
        {
            "start_time": 0.0,
            "end_time": 45.0,
            "speaker": "Speaker 1",
            "confidence_score": 0.92,
            "tone": "neutral",
            "transcript": "Good afternoon everyone. Thank you for joining us for our Q4 2024 earnings call. We're thrilled to report another record quarter.",
        },
        {
            "start_time": 45.0,
            "end_time": 120.0,
            "speaker": "Speaker 2",
            "confidence_score": 0.88,
            "tone": "neutral",
            "transcript": "Total revenue for the quarter reached $110.2 billion, up 23% year over year. Our Services business continues to accelerate.",
        },
        {
            "start_time": 120.0,
            "end_time": 180.0,
            "speaker": "Speaker 1",
            "confidence_score": 0.85,
            "tone": "happy",
            "transcript": "Our product pipeline has never been stronger. We're seeing incredible adoption of our AI features across the ecosystem.",
        },
        {
            "start_time": 180.0,
            "end_time": 240.0,
            "speaker": "Speaker 3",
            "confidence_score": 0.78,
            "tone": "neutral",
            "transcript": "Can you speak to the margin pressure we're seeing in the hardware segment? What's the outlook for next quarter?",
        },
        {
            "start_time": 240.0,
            "end_time": 300.0,
            "speaker": "Speaker 1",
            "confidence_score": 0.65,
            "tone": "neutral",
            "transcript": "We're always looking at ways to optimize our cost structure. The overall picture is very positive and we remain confident in our trajectory.",
        },
        {
            "start_time": 300.0,
            "end_time": 360.0,
            "speaker": "Speaker 2",
            "confidence_score": 0.82,
            "tone": "neutral",
            "transcript": "Gross margins came in at 46.2%, slightly below expectations due to component costs, but we expect improvement in Q1.",
        },
        {
            "start_time": 360.0,
            "end_time": 420.0,
            "speaker": "Speaker 4",
            "confidence_score": 0.75,
            "tone": "neutral",
            "transcript": "What's driving the acceleration in Services revenue? Can you break down the contribution from the App Store versus subscriptions?",
        },
        {
            "start_time": 420.0,
            "end_time": 480.0,
            "speaker": "Speaker 1",
            "confidence_score": 0.91,
            "tone": "happy",
            "transcript": "Services is truly a growth engine for us. We now have over 1 billion paid subscriptions across our platform. The ecosystem flywheel is working.",
        },
    ]
    return segments
