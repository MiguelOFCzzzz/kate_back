from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import bcrypt

from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado."
        )

    password_hash = bcrypt.hashpw(
        user_data.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=password_hash,
        birth_date=user_data.birth_date,
        height_cm=user_data.height_cm,
        weight_kg=user_data.weight_kg
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_data.name is not None:
        current_user.name = user_data.name

    if user_data.birth_date is not None:
        current_user.birth_date = user_data.birth_date

    if user_data.height_cm is not None:
        current_user.height_cm = user_data.height_cm

    if user_data.weight_kg is not None:
        current_user.weight_kg = user_data.weight_kg

    db.commit()
    db.refresh(current_user)

    return current_user