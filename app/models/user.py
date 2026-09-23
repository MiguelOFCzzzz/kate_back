from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    height_cm: Mapped[float | None] = mapped_column(Float, nullable=True)

    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    body_assessments = relationship(
        "BodyAssessment",
        back_populates="user"
    )

    nutrition_goals = relationship(
        "NutritionGoal",
        back_populates="user"
    )

    meals = relationship(
        "Meal",
        back_populates="user"
    )