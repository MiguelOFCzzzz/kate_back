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

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.meal import Meal
from app.models.meal_item import MealItem
from app.models.user import User
from app.schemas.meal import (
    MealCreate,
    MealResponse,
    MealDayResponse
)
from datetime import date
from app.services.meal_ai_service import analyze_meal_image


router = APIRouter(
    prefix="/meals",
    tags=["Meals"]
)


UPLOAD_DIR = Path("uploads/meals")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}


@router.post(
    "/analyze",
    status_code=status.HTTP_200_OK
)
async def analyze_meal(
    image: UploadFile = File(...),
    ingredients: str | None = Form(None),
    comment: str | None = Form(None),
    current_user: User = Depends(get_current_user)
):
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

    try:
        ai_result = await analyze_meal_image(
            image_bytes=image_bytes,
            mime_type=image.content_type,
            ingredients=ingredients,
            comment=comment
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erro ao analisar a refeição com a IA: {str(e)}"
        )

    return {
        "user_id": current_user.id,
        "image_path": str(file_path),
        "ingredients": ingredients,
        "comment": comment,
        "analysis": ai_result
    }


@router.get(
    "/me",
    response_model=list[MealResponse]
)
async def get_my_meals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meals = (
        db.query(Meal)
        .filter(Meal.user_id == current_user.id)
        .order_by(Meal.created_at.desc())
        .all()
    )

    return meals


@router.post(
    "/",
    response_model=MealResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_meal(
    meal_data: MealCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not meal_data.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A refeição precisa ter pelo menos um alimento."
        )

    total_calories = sum(
        item.calories
        for item in meal_data.items
    )

    total_protein_g = sum(
        item.protein_g
        for item in meal_data.items
    )

    total_carbohydrates_g = sum(
        item.carbohydrates_g
        for item in meal_data.items
    )

    total_fats_g = sum(
        item.fats_g
        for item in meal_data.items
    )

    meal = Meal(
        user_id=current_user.id,
        meal_type=meal_data.meal_type,
        image_path=meal_data.image_path,
        total_calories=total_calories,
        total_protein_g=total_protein_g,
        total_carbohydrates_g=total_carbohydrates_g,
        total_fats_g=total_fats_g
    )

    db.add(meal)
    db.flush()

    for item in meal_data.items:
        meal_item = MealItem(
            meal_id=meal.id,
            food_id=item.food_id,
            food_name=item.food_name,
            estimated_weight_g=item.estimated_weight_g,
            calories=item.calories,
            protein_g=item.protein_g,
            carbohydrates_g=item.carbohydrates_g,
            fats_g=item.fats_g
        )

        db.add(meal_item)

    db.commit()
    db.refresh(meal)

    return meal
@router.get(
    "/day",
    response_model=MealDayResponse
)
async def get_meals_by_day(
    date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    meals = (
        db.query(Meal)
        .filter(
            Meal.user_id == current_user.id,
            Meal.created_at >= date,
            Meal.created_at < date.fromordinal(date.toordinal() + 1)
        )
        .order_by(Meal.created_at.asc())
        .all()
    )

    total_calories = sum(
        meal.total_calories for meal in meals
    )

    total_protein_g = sum(
        meal.total_protein_g for meal in meals
    )

    total_carbohydrates_g = sum(
        meal.total_carbohydrates_g for meal in meals
    )

    total_fats_g = sum(
        meal.total_fats_g for meal in meals
    )

    return {
        "date": date.isoformat(),
        "meals": meals,
        "total_calories": total_calories,
        "total_protein_g": total_protein_g,
        "total_carbohydrates_g": total_carbohydrates_g,
        "total_fats_g": total_fats_g
    }

@router.post(
    "/{meal_id}/repeat",
    response_model=MealResponse,
    status_code=status.HTTP_201_CREATED
)
async def repeat_meal(
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    original_meal = (
        db.query(Meal)
        .filter(
            Meal.id == meal_id,
            Meal.user_id == current_user.id
        )
        .first()
    )

    if not original_meal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refeição não encontrada."
        )

    original_items = (
        db.query(MealItem)
        .filter(MealItem.meal_id == original_meal.id)
        .all()
    )

    new_meal = Meal(
        user_id=current_user.id,
        meal_type=original_meal.meal_type,
        image_path=original_meal.image_path,
        total_calories=original_meal.total_calories,
        total_protein_g=original_meal.total_protein_g,
        total_carbohydrates_g=original_meal.total_carbohydrates_g,
        total_fats_g=original_meal.total_fats_g
    )

    db.add(new_meal)
    db.flush()

    for original_item in original_items:
        new_item = MealItem(
            meal_id=new_meal.id,
            food_id=original_item.food_id,
            food_name=original_item.food_name,
            estimated_weight_g=original_item.estimated_weight_g,
            calories=original_item.calories,
            protein_g=original_item.protein_g,
            carbohydrates_g=original_item.carbohydrates_g,
            fats_g=original_item.fats_g
        )

        db.add(new_item)

    db.commit()
    db.refresh(new_meal)

    return new_meal