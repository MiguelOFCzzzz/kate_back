from datetime import datetime

from pydantic import BaseModel


class BodyMeasurementCreate(BaseModel):
    weight_kg: float
    body_fat_percent: float | None = None


class BodyMeasurementResponse(BaseModel):
    id: int
    user_id: int
    weight_kg: float
    body_fat_percent: float | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True