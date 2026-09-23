from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class BodyAssessment(Base):
    __tablename__ = "body_assessments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    image_path: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    estimated_body_fat: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    recommended_strategy: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    user_goal: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    weekly_exercise_frequency: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    ai_analysis: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="body_assessments"
    )

    nutrition_goals = relationship(
        "NutritionGoal",
        back_populates="body_assessment"
    )