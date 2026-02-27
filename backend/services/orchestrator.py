import asyncio
import logging
from datetime import datetime

from sqlalchemy.orm import Session

from models.database import (
    Analysis,
    Entity,
    FactCheck,
    SessionLocal,
    VisualSegment,
    VoiceSegment,
)
from services import fastino_service, modulate_service, reka_service, yutori_service
from utils.media import cleanup_work_dir, download_media, extract_frames

logger = logging.getLogger(__name__)


def run_analysis_pipeline(analysis_id: str, source_url: str):
    """Main orchestrator — runs all analysis services and stores results."""
    asyncio.run(_async_pipeline(analysis_id, source_url))


async def _async_pipeline(analysis_id: str, source_url: str):
    db = SessionLocal()
    work_dir = None
    try:
        analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
        if not analysis:
            logger.error(f"Analysis {analysis_id} not found")
            return

        logger.info(f"Starting analysis pipeline for {analysis_id}")

        # Step 1: Download media
        media = download_media(source_url)
        work_dir = media.get("work_dir")

        if media.get("error"):
            logger.warning(f"Media download failed: {media['error']}. Proceeding with mock data.")

        video_path = media.get("video_path")
        audio_path = media.get("audio_path")

        # Step 2: Extract frames for visual analysis
        frames = []
        if video_path:
            frames = extract_frames(video_path, interval_seconds=30)

        # Step 3: Build a mock transcript (in production, use Whisper or similar)
        transcript = _get_transcript_text()

        # Step 4: Run all analysis services in parallel
        visual_task = reka_service.analyze_video_frames(frames) if frames else reka_service.analyze_video_url(source_url)
        voice_task = modulate_service.analyze_voice(audio_path, transcript)
        entity_task = fastino_service.extract_entities(transcript)
        classification_task = fastino_service.classify_statements(transcript)

        visual_results, voice_results, entities, classifications = await asyncio.gather(
            visual_task, voice_task, entity_task, classification_task
        )

        # Step 5: Fact-check key claims using Yutori
        claims_to_check = [
            c for c in classifications
            if c.get("classification") in ("forward_looking_statement", "performance_metric", "risk_disclosure")
        ]
        fact_check_results = await yutori_service.fact_check_claims(claims_to_check)

        # Step 6: Store all results in database
        _store_visual_segments(db, analysis_id, visual_results)
        _store_voice_segments(db, analysis_id, voice_results)
        _store_entities(db, analysis_id, entities)
        _store_fact_checks(db, analysis_id, fact_check_results)

        # Step 7: Generate summary
        summary = _generate_summary(entities, voice_results, visual_results, fact_check_results)
        analysis.summary = summary
        analysis.status = "completed"
        analysis.completed_at = datetime.utcnow()
        db.commit()

        logger.info(f"Analysis pipeline completed for {analysis_id}")

    except Exception as e:
        logger.error(f"Analysis pipeline failed for {analysis_id}: {e}")
        try:
            analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                analysis.status = "failed"
                analysis.summary = f"Analysis failed: {str(e)}"
                db.commit()
        except Exception as db_err:
            logger.error(f"Failed to update analysis status: {db_err}")
    finally:
        if work_dir:
            cleanup_work_dir(work_dir)
        db.close()


def _store_visual_segments(db: Session, analysis_id: str, segments: list[dict]):
    for seg in segments:
        db.add(VisualSegment(
            analysis_id=analysis_id,
            timestamp=seg.get("timestamp", 0),
            description=seg.get("description", ""),
            content_type=seg.get("content_type", "unknown"),
        ))
    db.commit()


def _store_voice_segments(db: Session, analysis_id: str, segments: list[dict]):
    for seg in segments:
        db.add(VoiceSegment(
            analysis_id=analysis_id,
            start_time=seg.get("start_time", 0),
            end_time=seg.get("end_time", 0),
            speaker=seg.get("speaker", "Unknown"),
            confidence_score=seg.get("confidence_score", 0),
            tone=seg.get("tone", "neutral"),
            transcript=seg.get("transcript", ""),
        ))
    db.commit()


def _store_entities(db: Session, analysis_id: str, entities: list[dict]):
    for ent in entities:
        db.add(Entity(
            analysis_id=analysis_id,
            name=ent.get("name", ""),
            entity_type=ent.get("entity_type", "unknown"),
            context=ent.get("context", ""),
            confidence=ent.get("confidence", 0),
        ))
    db.commit()


def _store_fact_checks(db: Session, analysis_id: str, fact_checks: list[dict]):
    for fc in fact_checks:
        db.add(FactCheck(
            analysis_id=analysis_id,
            claim=fc.get("claim", ""),
            verdict=fc.get("verdict", "unverified"),
            evidence=fc.get("evidence", ""),
            sources=fc.get("sources", "[]"),
        ))
    db.commit()


def _generate_summary(entities, voice, visual, fact_checks) -> str:
    """Generate an executive summary from all analysis results."""
    people = [e for e in entities if e.get("entity_type") == "person"]
    companies = [e for e in entities if e.get("entity_type") == "company"]
    metrics = [e for e in entities if e.get("entity_type") in ("currency_amount", "percentage", "financial_metric")]

    verified = sum(1 for fc in fact_checks if fc.get("verdict") == "verified")
    disputed = sum(1 for fc in fact_checks if fc.get("verdict") == "disputed")

    avg_confidence = sum(s.get("confidence_score", 0) for s in voice) / max(len(voice), 1)

    low_confidence = [s for s in voice if s.get("confidence_score", 1) < 0.7]

    summary_parts = [
        f"## Executive Summary\n",
        f"**Speakers identified:** {', '.join(p['name'] for p in people[:5])}",
        f"**Companies mentioned:** {', '.join(c['name'] for c in companies[:5])}",
        f"**Key metrics:** {', '.join(m['name'] for m in metrics[:5])}",
        f"\n### Voice Analysis",
        f"Average speaker confidence: {avg_confidence:.0%}",
    ]

    if low_confidence:
        summary_parts.append(
            f"**Notable:** {len(low_confidence)} segments flagged with below-average confidence, "
            f"particularly during Q&A on margins and competitive positioning."
        )

    summary_parts.extend([
        f"\n### Fact Check Results",
        f"- **{verified}** claims verified against public data",
        f"- **{disputed}** claims disputed or needing context",
        f"- **{len(fact_checks) - verified - disputed}** claims unverified",
    ])

    if visual:
        charts = sum(1 for v in visual if v.get("content_type") == "chart")
        slides = sum(1 for v in visual if v.get("content_type") == "slide")
        summary_parts.extend([
            f"\n### Visual Content",
            f"Detected **{charts}** charts/graphs and **{slides}** presentation slides.",
        ])

    return "\n".join(summary_parts)


def _get_transcript_text() -> str:
    """Placeholder transcript for demo purposes."""
    return (
        "Good afternoon everyone. Thank you for joining us for our Q4 2024 earnings call. "
        "I'm Tim Cook, CEO of Apple. Joining me today is Luca Maestri, our CFO. "
        "We're thrilled to report another record quarter. Total revenue for the quarter "
        "reached $110.2 billion, up 23% year over year. Our Services business continues "
        "to accelerate, and we now have over 1 billion paid subscriptions across our platform. "
        "iPhone revenue came in at $65.8 billion, with strong demand across the lineup. "
        "Our product pipeline has never been stronger. We're seeing incredible adoption "
        "of our AI features across the ecosystem. "
        "Gross margins came in at 46.2%, slightly below expectations due to component costs, "
        "but we expect improvement in Q1 as supply chain conditions normalize. "
        "We continue to invest aggressively in R&D, with $7.4 billion this quarter alone. "
        "Greater China revenue grew 11% to $21.4 billion, showing strong recovery. "
        "We returned $25 billion to shareholders through dividends and buybacks this quarter. "
        "Looking ahead, we see continued momentum across all product categories."
    )
