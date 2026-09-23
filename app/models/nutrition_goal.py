from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class NutritionGoal(Base):
    __tablename__ = "nutrition_goals"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    body_assessment_id: Mapped[int | None] = mapped_column(
        ForeignKey("body_assessments.id"),
        nullable=True
    )

    strategy: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    daily_calories: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    protein_g: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    carbohydrates_g: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    fats_g: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="nutrition_goals"
    )

    body_assessment = relationship(
        "BodyAssessment",
        back_populates="nutrition_goals"
    )