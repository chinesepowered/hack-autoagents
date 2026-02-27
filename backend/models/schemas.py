from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AnalyzeRequest(BaseModel):
    url: str


class AnalyzeResponse(BaseModel):
    analysis_id: str
    status: str


class EntityOut(BaseModel):
    id: str
    name: str
    entity_type: Optional[str] = None
    context: Optional[str] = None
    confidence: Optional[float] = None

    class Config:
        from_attributes = True


class VoiceSegmentOut(BaseModel):
    id: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    speaker: Optional[str] = None
    confidence_score: Optional[float] = None
    tone: Optional[str] = None
    transcript: Optional[str] = None

    class Config:
        from_attributes = True


class VisualSegmentOut(BaseModel):
    id: str
    timestamp: Optional[float] = None
    frame_url: Optional[str] = None
    description: Optional[str] = None
    content_type: Optional[str] = None

    class Config:
        from_attributes = True


class FactCheckOut(BaseModel):
    id: str
    claim: str
    verdict: Optional[str] = None
    evidence: Optional[str] = None
    sources: Optional[str] = None

    class Config:
        from_attributes = True


class AnalysisOut(BaseModel):
    id: str
    title: Optional[str] = None
    source_url: Optional[str] = None
    status: str
    summary: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    entities: list[EntityOut] = []
    voice_segments: list[VoiceSegmentOut] = []
    visual_segments: list[VisualSegmentOut] = []
    fact_checks: list[FactCheckOut] = []

    class Config:
        from_attributes = True


class StatusOut(BaseModel):
    id: str
    status: str
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
