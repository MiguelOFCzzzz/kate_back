from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.strategy_ai_service import generate_strategy_analysis

router = APIRouter(
    prefix="/ai-strategy",
    tags=["AI Strategy"]
)


@router.post("/analyze")
def analyze_strategy(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        analysis = generate_strategy_analysis(
            db=db,
            user_id=current_user.id
        )

        return {
            "user_id": current_user.id,
            "should_reevaluate": analysis["should_reevaluate"],
            "reason": analysis["reason"],
            "suggested_strategy": analysis["suggested_strategy"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Erro ao analisar estratégia com a IA: {str(e)}"
        )