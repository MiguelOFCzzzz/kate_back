from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.body_assessment import BodyAssessment
from app.models.user import User
from app.services.nutrition_service import calculate_nutrition_suggestion


router = APIRouter(
    prefix="/nutrition-goals",
    tags=["Nutrition Goals"]
)


@router.get("/suggestion")
async def get_nutrition_suggestion(
    weekly_exercise_frequency: int,
    strategy: str | None = None,
    body_assessment_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user.birth_date:
        raise HTTPException(
            status_code=400,
            detail="Data de nascimento não cadastrada."
        )

    if current_user.weight_kg is None:
        raise HTTPException(
            status_code=400,
            detail="Peso não cadastrado."
        )

    if current_user.height_cm is None:
        raise HTTPException(
            status_code=400,
            detail="Altura não cadastrada."
        )

    today = date.today()

    age = today.year - current_user.birth_date.year

    if (today.month, today.day) < (
        current_user.birth_date.month,
        current_user.birth_date.day
    ):
        age -= 1

    assessment = None

    if body_assessment_id is not None:
        assessment = (
            db.query(BodyAssessment)
            .filter(
                BodyAssessment.id == body_assessment_id,
                BodyAssessment.user_id == current_user.id
            )
            .first()
        )

        if not assessment:
            raise HTTPException(
                status_code=404,
                detail="Avaliação corporal não encontrada."
            )

        # Se a estratégia não foi enviada manualmente,
        # usamos a estratégia sugerida pela IA.
        if strategy is None:
            strategy = assessment.recommended_strategy

    if strategy is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Informe uma estratégia ou forneça "
                "uma avaliação corporal com estratégia."
            )
        )

    try:
        suggestion = calculate_nutrition_suggestion(
            weight_kg=current_user.weight_kg,
            height_cm=current_user.height_cm,
            age=age,
            weekly_exercise_frequency=weekly_exercise_frequency,
            strategy=strategy
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "available": True,
        "is_estimate": True,
        "disclaimer": (
            "Esta é uma estimativa gerada pelo aplicativo para "
            "orientação e planejamento. Não representa uma prescrição "
            "nutricional e não deve ser seguida como uma regra exata."
        ),
        "user_id": current_user.id,
        "body_assessment_id": (
            assessment.id if assessment else None
        ),
        "age": age,
        "suggestion": suggestion
    }