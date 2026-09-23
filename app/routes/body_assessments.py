from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.body_assessment import BodyAssessment
from app.models.user import User
from app.schemas.body_assessment import BodyAssessmentResponse
from app.services.ai_service import analyze_body_image


router = APIRouter(
    prefix="/body-assessments",
    tags=["Body Assessments"]
)


UPLOAD_DIR = Path("uploads/body_assessments")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}


@router.post(
    "/",
    response_model=BodyAssessmentResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_body_assessment(
    user_goal: str | None = Form(None),
    weekly_exercise_frequency: int | None = Form(None),
    image: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    image_path = None
    ai_result = None

    if image:
        if image.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de imagem não permitido. Use JPG, PNG ou WEBP."
            )

        extension = Path(image.filename or "").suffix.lower()

        if not extension:
            extension = ".jpg"

        filename = f"{uuid4()}{extension}"
        file_path = UPLOAD_DIR / filename

        image_bytes = await image.read()

        file_path.write_bytes(image_bytes)

        image_path = str(file_path)

        try:
            ai_result = await analyze_body_image(
                image_bytes=image_bytes,
                mime_type=image.content_type,
                user_goal=user_goal,
                weekly_exercise_frequency=weekly_exercise_frequency
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Erro ao analisar a imagem com a IA: {str(e)}"
            )

    assessment = BodyAssessment(
        user_id=current_user.id,
        image_path=image_path,
        estimated_body_fat=(
            ai_result.get("estimated_body_fat")
            if ai_result
            else None
        ),
        recommended_strategy=(
            ai_result.get("recommended_strategy")
            if ai_result
            else None
        ),
        user_goal=user_goal,
        weekly_exercise_frequency=weekly_exercise_frequency,
        ai_analysis=(
            str(ai_result)
            if ai_result
            else None
        )
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return assessment


@router.get(
    "/me",
    response_model=list[BodyAssessmentResponse]
)
async def get_my_body_assessments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessments = (
        db.query(BodyAssessment)
        .filter(BodyAssessment.user_id == current_user.id)
        .order_by(BodyAssessment.created_at.desc())
        .all()
    )

    return assessments


@router.get("/{assessment_id}/image")
async def get_body_assessment_image(
    assessment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assessment = (
        db.query(BodyAssessment)
        .filter(
            BodyAssessment.id == assessment_id,
            BodyAssessment.user_id == current_user.id
        )
        .first()
    )

    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="Avaliação corporal não encontrada."
        )

    if not assessment.image_path:
        raise HTTPException(
            status_code=404,
            detail="Esta avaliação não possui uma imagem."
        )

    file_path = Path(assessment.image_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Arquivo de imagem não encontrado."
        )

    return FileResponse(file_path)