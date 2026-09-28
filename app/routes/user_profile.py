from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user_profile import UserProfile
from app.schemas.user_profile import (
    UserProfileCreate,
    UserProfileResponse,
)

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


@router.get(
    "/me",
    response_model=UserProfileResponse
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Perfil não encontrado."
        )

    return profile


@router.post(
    "/me",
    response_model=UserProfileResponse
)
def create_or_update_my_profile(
    data: UserProfileCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == current_user.id)
        .first()
    )

    if profile:
        profile.goal = data.goal
        profile.exercise_frequency = data.exercise_frequency
        profile.exercise_intensity = data.exercise_intensity
    else:
        profile = UserProfile(
            user_id=current_user.id,
            goal=data.goal,
            exercise_frequency=data.exercise_frequency,
            exercise_intensity=data.exercise_intensity
        )

        db.add(profile)

    db.commit()
    db.refresh(profile)

    return profile