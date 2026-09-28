from datetime import date, datetime

from pydantic import BaseModel


class CurrentStrategyCreate(BaseModel):
    strategy: str
    protein_goal_g: float
    start_date: date
    end_date: date | None = None


class CurrentStrategyResponse(BaseModel):
    id: int
    user_id: int
    strategy: str
    protein_goal_g: float
    start_date: date
    end_date: date | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True