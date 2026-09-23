from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    meal_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    image_path: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    total_calories: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    total_protein_g: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    total_carbohydrates_g: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    total_fats_g: Mapped[float] = mapped_column(
        Float,
        default=0
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
        back_populates="meals"
    )

    items = relationship(
        "MealItem",
        back_populates="meal",
        cascade="all, delete-orphan"
    )