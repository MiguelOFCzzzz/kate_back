from google import genai
from sqlalchemy.orm import Session

from app.config import settings
from app.models.body_measurement import BodyMeasurement
from app.models.user_profile import UserProfile


client = genai.Client(api_key=settings.GEMINI_API_KEY)


def get_progress_context(db: Session, user_id: int):
    profile = (
        db.query(UserProfile)
        .filter(UserProfile.user_id == user_id)
        .first()
    )

    measurements = (
        db.query(BodyMeasurement)
        .filter(BodyMeasurement.user_id == user_id)
        .order_by(BodyMeasurement.created_at.asc())
        .all()
    )

    return {
        "profile": profile,
        "measurements": measurements
    }


def generate_progress_analysis(db: Session, user_id: int):
    context = get_progress_context(db, user_id)

    profile = context["profile"]
    measurements = context["measurements"]

    if not measurements:
        return "Ainda não existem medições suficientes para analisar o progresso."

    measurements_text = "\n".join(
        [
            (
                f"- Data: {measurement.created_at.date()}, "
                f"peso: {measurement.weight_kg} kg, "
                f"percentual de gordura: "
                f"{measurement.body_fat_percent if measurement.body_fat_percent is not None else 'não informado'}"
            )
            for measurement in measurements
        ]
    )

    goal = profile.goal if profile else "não informado"

    frequency = (
        profile.exercise_frequency
        if profile and profile.exercise_frequency is not None
        else "não informado"
    )

    intensity = (
        profile.exercise_intensity
        if profile and profile.exercise_intensity
        else "não informado"
    )

    prompt = f"""
Você é um assistente de acompanhamento de progresso físico.

Analise os dados fornecidos de forma descritiva e cuidadosa.
Não faça diagnóstico médico.
Não trate estimativas de composição corporal como medidas exatas.
Não recomende dietas restritivas ou mudanças extremas.

Objetivo informado pelo usuário:
{goal}

Frequência de exercícios:
{frequency}

Intensidade dos exercícios:
{intensity}

Histórico de medições:
{measurements_text}

Compare as medições ao longo do tempo e responda:

1. O que mudou no histórico?
2. Quais tendências podem ser observadas?
3. O que merece acompanhamento na próxima medição?
"""

    models = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-2.5-flash",
    ]

    last_error = None

    for model in models:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            return response.text

        except Exception as error:
            last_error = error

    if last_error:
        raise last_error

    return "Não foi possível gerar a análise."