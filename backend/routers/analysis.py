import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from models.database import Analysis, get_db
from models.schemas import AnalyzeRequest, AnalyzeResponse, AnalysisOut, StatusOut
from services.orchestrator import run_analysis_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


@router.post("/analyze", response_model=AnalyzeResponse)
async def create_analysis(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    analysis = Analysis(source_url=request.url, title=f"Analysis of {request.url[:60]}")
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    background_tasks.add_task(run_analysis_pipeline, analysis.id, request.url)

    return AnalyzeResponse(analysis_id=analysis.id, status="processing")


@router.get("/analysis/{analysis_id}", response_model=AnalysisOut)
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis


@router.get("/analysis/{analysis_id}/status", response_model=StatusOut)
def get_analysis_status(analysis_id: str, db: Session = Depends(get_db)):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return StatusOut(
        id=analysis.id,
        status=analysis.status,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
    )


@router.get("/analyses", response_model=list[AnalysisOut])
def list_analyses(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    analyses = (
        db.query(Analysis)
        .order_by(Analysis.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return analyses
