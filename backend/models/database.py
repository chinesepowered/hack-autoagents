import uuid

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    create_engine,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

from config import settings


class Base(DeclarativeBase):
    pass


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(Text)
    source_url = Column(Text)
    status = Column(String(20), default="processing")
    summary = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)

    entities = relationship("Entity", back_populates="analysis", cascade="all, delete-orphan")
    voice_segments = relationship("VoiceSegment", back_populates="analysis", cascade="all, delete-orphan")
    visual_segments = relationship("VisualSegment", back_populates="analysis", cascade="all, delete-orphan")
    fact_checks = relationship("FactCheck", back_populates="analysis", cascade="all, delete-orphan")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.id"), nullable=False)
    name = Column(Text, nullable=False)
    entity_type = Column(String(50))
    context = Column(Text)
    confidence = Column(Float)

    analysis = relationship("Analysis", back_populates="entities")


class VoiceSegment(Base):
    __tablename__ = "voice_segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.id"), nullable=False)
    start_time = Column(Float)
    end_time = Column(Float)
    speaker = Column(String(100))
    confidence_score = Column(Float)
    tone = Column(String(50))
    transcript = Column(Text)

    analysis = relationship("Analysis", back_populates="voice_segments")


class VisualSegment(Base):
    __tablename__ = "visual_segments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.id"), nullable=False)
    timestamp = Column(Float)
    frame_url = Column(Text)
    description = Column(Text)
    content_type = Column(String(50))

    analysis = relationship("Analysis", back_populates="visual_segments")


class FactCheck(Base):
    __tablename__ = "fact_checks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = Column(String(36), ForeignKey("analyses.id"), nullable=False)
    claim = Column(Text, nullable=False)
    verdict = Column(String(30))
    evidence = Column(Text)
    sources = Column(Text)  # JSON string

    analysis = relationship("Analysis", back_populates="fact_checks")


engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
