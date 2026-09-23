from fastapi import FastAPI
from sqlalchemy import text
from app.routes.auth import router as auth_router
from app.routes.nutrition_goals import router as nutrition_goals_router
from app.routes.users import router as users_router
from app.routes.body_assessments import router as body_assessments_router
from app.database.database import engine
from app.routes.meals import router as meals_router
from app.routes.nutrition_suggestions import router as nutrition_suggestions_router
from app.database.base import Base
from app.models import (
    User,
    BodyAssessment,
    NutritionGoal,
    Food,
    Meal,
    MealItem,
)


app = FastAPI(
    title="Kate App API",
    description="API do aplicativo de nutrição e fitness",
    version="1.0.0"
)

app.include_router(meals_router)
app.include_router(nutrition_suggestions_router)
app.include_router(body_assessments_router)
app.include_router(nutrition_goals_router)
app.include_router(users_router)
app.include_router(auth_router)

Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Kate App API funcionando!"}


@app.get("/teste-db")
async def teste_db():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {"message": "MySQL conectado com sucesso!"}

    except Exception as e:
        return {
            "message": "Erro ao conectar com o MySQL",
            "error": str(e)
        }