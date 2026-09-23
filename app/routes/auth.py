from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import bcrypt

from app.database.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import create_access_token


router = APIRouter(prefix="/login", tags=["Authentication"])


@router.post("/", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == login_data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos."
        )

    password_correct = bcrypt.checkpw(
        login_data.password.encode("utf-8"),
        user.password_hash.encode("utf-8")
    )

    if not password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos."
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }