from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class MealItem(Base):
    __tablename__ = "meal_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    meal_id: Mapped[int] = mapped_column(
        ForeignKey("meals.id"),
        nullable=False
    )

    food_id: Mapped[int | None] = mapped_column(
        ForeignKey("foods.id"),
        nullable=True
    )

    food_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    estimated_weight_g: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    calories: Mapped[float] = mapped_column(
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

    meal = relationship(
        "Meal",
        back_populates="items"
    )

    food = relationship(
        "Food",
        back_populates="meal_items"
    )