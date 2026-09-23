from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Food(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    calories_per_100g: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    protein_per_100g: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    carbohydrates_per_100g: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    fats_per_100g: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    meal_items = relationship(
        "MealItem",
        back_populates="food"
    )