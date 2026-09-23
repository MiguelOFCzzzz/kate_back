from datetime import date

from pydantic import BaseModel


class NutritionGoalCreate(BaseModel):
    body_assessment_id: int | None = None
    strategy: str
    daily_calories: float
    protein_g: float
    carbohydrates_g: float
    fats_g: float
    start_date: date
    end_date: date | None = None


class NutritionGoalResponse(BaseModel):
    id: int
    user_id: int
    body_assessment_id: int | None
    strategy: str
    daily_calories: float
    protein_g: float
    carbohydrates_g: float
    fats_g: float
    start_date: date
    end_date: date | None

    class Config:
        from_attributes = True