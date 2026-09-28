from typing import Literal

from pydantic import BaseModel


MealType = Literal[
    "cafe_da_manha",
    "almoco",
    "pre_treino",
    "jantar"
]


class MealItemCreate(BaseModel):
    food_id: int | None = None
    food_name: str
    estimated_weight_g: float
    calories: float
    protein_g: float
    carbohydrates_g: float
    fats_g: float


class MealCreate(BaseModel):
    meal_type: MealType
    image_path: str | None = None
    items: list[MealItemCreate]


class MealItemResponse(BaseModel):
    id: int
    food_id: int | None
    food_name: str
    estimated_weight_g: float
    calories: float
    protein_g: float
    carbohydrates_g: float
    fats_g: float

    class Config:
        from_attributes = True


class MealResponse(BaseModel):
    id: int
    user_id: int
    meal_type: str
    image_path: str | None
    total_calories: float
    total_protein_g: float
    total_carbohydrates_g: float
    total_fats_g: float
    items: list[MealItemResponse]

    class Config:
        from_attributes = True

class MealDayResponse(BaseModel):
    date: str
    meals: list[MealResponse]
    total_calories: float
    total_protein_g: float
    total_carbohydrates_g: float
    total_fats_g: float