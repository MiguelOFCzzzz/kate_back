from datetime import datetime

from pydantic import BaseModel


class UserProfileCreate(BaseModel):
    goal: str | None = None
    exercise_frequency: int | None = None
    exercise_intensity: str | None = None


class UserProfileResponse(BaseModel):
    id: int
    user_id: int
    goal: str | None
    exercise_frequency: int | None
    exercise_intensity: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True