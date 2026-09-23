from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.body_assessment import BodyAssessment
from app.models.nutrition_goal import NutritionGoal
from app.models.user import User
from app.schemas.nutrition_goal import (
    NutritionGoalCreate,
    NutritionGoalResponse
)


router = APIRouter(
    prefix="/nutrition-goals",
    tags=["Nutrition Goals"]
)


@router.post(
    "/",
    response_model=NutritionGoalResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_nutrition_goal(
    goal_data: NutritionGoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if goal_data.body_assessment_id is not None:
        assessment = (
            db.query(BodyAssessment)
            .filter(
                BodyAssessment.id == goal_data.body_assessment_id,
                BodyAssessment.user_id == current_user.id
            )
            .first()
        )

        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Avaliação corporal não encontrada."
            )

    goal = NutritionGoal(
        user_id=current_user.id,
        body_assessment_id=goal_data.body_assessment_id,
        strategy=goal_data.strategy,
        daily_calories=goal_data.daily_calories,
        protein_g=goal_data.protein_g,
        carbohydrates_g=goal_data.carbohydrates_g,
        fats_g=goal_data.fats_g,
        start_date=goal_data.start_date,
        end_date=goal_data.end_date
    )

    db.add(goal)
    db.commit()
    db.refresh(goal)

    return goal


@router.get(
    "/me",
    response_model=list[NutritionGoalResponse]
)
async def get_my_nutrition_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    goals = (
        db.query(NutritionGoal)
        .filter(NutritionGoal.user_id == current_user.id)
        .order_by(NutritionGoal.start_date.desc())
        .all()
    )

    return goals