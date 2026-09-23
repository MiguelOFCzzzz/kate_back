from pydantic import BaseModel


class BodyAssessmentCreate(BaseModel):
    user_goal: str | None = None
    weekly_exercise_frequency: int | None = None


class BodyAssessmentResponse(BaseModel):
    id: int
    user_id: int
    image_path: str | None
    estimated_body_fat: float | None
    recommended_strategy: str | None
    user_goal: str | None
    weekly_exercise_frequency: int | None
    ai_analysis: str | None

    class Config:
        from_attributes = True