from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.current_strategy import CurrentStrategy
from app.models.meal import Meal
from app.models.user import User


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/today")
def get_today_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    tomorrow = today + timedelta(days=1)

    meals = (
        db.query(Meal)
        .filter(
            Meal.user_id == current_user.id,
            Meal.created_at >= today,
            Meal.created_at < tomorrow
        )
        .all()
    )

    protein_consumed_g = sum(
        meal.total_protein_g for meal in meals
    )

    current_strategy = (
        db.query(CurrentStrategy)
        .filter(
            CurrentStrategy.user_id == current_user.id,
            CurrentStrategy.end_date.is_(None)
        )
        .order_by(CurrentStrategy.created_at.desc())
        .first()
    )

    protein_goal_g = (
        current_strategy.protein_goal_g
        if current_strategy
        else None
    )

    return {
        "date": today.isoformat(),
        "protein_consumed_g": protein_consumed_g,
        "protein_goal_g": protein_goal_g,
        "meals_count": len(meals)
    }