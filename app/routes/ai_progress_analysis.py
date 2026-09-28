from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.ai_progress_analysis import AIProgressAnalysis
from app.schemas.ai_progress_analysis import (
    AIProgressAnalysisResponse,
)
from app.services.progress_ai_service import generate_progress_analysis


router = APIRouter(
    prefix="/ai-progress",
    tags=["AI Progress"]
)


@router.post(
    "/analyze",
    response_model=AIProgressAnalysisResponse
)
def analyze_my_progress(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    analysis_text = generate_progress_analysis(
        db=db,
        user_id=current_user.id
    )

    analysis = AIProgressAnalysis(
        user_id=current_user.id,
        analysis=analysis_text
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return analysis


@router.get(
    "/me",
    response_model=list[AIProgressAnalysisResponse]
)
def get_my_ai_progress_analyses(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    analyses = (
        db.query(AIProgressAnalysis)
        .filter(AIProgressAnalysis.user_id == current_user.id)
        .order_by(AIProgressAnalysis.created_at.desc())
        .all()
    )

    return analyses