from datetime import date, datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    birth_date: date | None = None
    height_cm: float | None = None
    weight_kg: float | None = None


class UserUpdate(BaseModel):
    name: str | None = None
    birth_date: date | None = None
    height_cm: float | None = None
    weight_kg: float | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    birth_date: date | None
    height_cm: float | None
    weight_kg: float | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)