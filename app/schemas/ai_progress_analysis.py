from datetime import datetime

from pydantic import BaseModel


class AIProgressAnalysisCreate(BaseModel):
    measurement_id: int | None = None
    analysis: str


class AIProgressAnalysisResponse(BaseModel):
    id: int
    user_id: int
    measurement_id: int | None
    analysis: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True