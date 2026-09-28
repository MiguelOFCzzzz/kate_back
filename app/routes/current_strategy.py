from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.current_strategy import CurrentStrategy
from app.schemas.current_strategy import (
    CurrentStrategyCreate,
    CurrentStrategyResponse
)

router = APIRouter(
    prefix="/strategy",
    tags=["Strategy"]
)


@router.get(
    "/me",
    response_model=CurrentStrategyResponse
)
def get_current_strategy(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    strategy = (
        db.query(CurrentStrategy)
        .filter(CurrentStrategy.user_id == current_user.id)
        .filter(CurrentStrategy.end_date.is_(None))
        .order_by(CurrentStrategy.created_at.desc())
        .first()
    )

    if not strategy:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma estratégia atual encontrada."
        )

    return strategy

@router.post(
    "/me",
    response_model=CurrentStrategyResponse
)
def create_current_strategy(
    data: CurrentStrategyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    current_strategy = (
        db.query(CurrentStrategy)
        .filter(CurrentStrategy.user_id == current_user.id)
        .filter(CurrentStrategy.end_date.is_(None))
        .order_by(CurrentStrategy.created_at.desc())
        .first()
    )

    # Se já existe uma estratégia atual,
    # encerramos a anterior no dia anterior à nova estratégia.
    if current_strategy:
        from datetime import timedelta

        current_strategy.end_date = (
            data.start_date - timedelta(days=1)
        )

    new_strategy = CurrentStrategy(
        user_id=current_user.id,
        strategy=data.strategy,
        protein_goal_g=data.protein_goal_g,
        start_date=data.start_date,
        end_date=data.end_date
    )

    db.add(new_strategy)
    db.commit()
    db.refresh(new_strategy)

    return new_strategy

@router.get(
    "/history",
    response_model=list[CurrentStrategyResponse]
)
def get_strategy_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    strategies = (
        db.query(CurrentStrategy)
        .filter(CurrentStrategy.user_id == current_user.id)
        .order_by(CurrentStrategy.start_date.desc())
        .all()
    )

    return strategies

  