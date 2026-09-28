import json

from google import genai
from sqlalchemy.orm import Session

from app.config import settings
from app.models.body_measurement import BodyMeasurement
from app.models.current_strategy import CurrentStrategy
from app.models.user_profile import UserProfile


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


def generate_strategy_analysis(db: Session, user_id: int):

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

    if len(measurements) < 2:
        return {
            "should_reevaluate": False,
            "reason": (
                "Ainda não existem medições suficientes para comparar "
                "a evolução ao longo do tempo."
            ),
            "suggested_strategy": None
        }

    current_strategy = (
        db.query(CurrentStrategy)
        .filter(CurrentStrategy.user_id == user_id)
        .filter(CurrentStrategy.end_date.is_(None))
        .order_by(CurrentStrategy.created_at.desc())
        .first()
    )

    measurements_text = "\n".join(
        [
            (
                f"- Data: {measurement.created_at.date()}, "
                f"peso: {measurement.weight_kg} kg, "
                f"percentual de gordura: "
                f"{measurement.body_fat_percent}"
            )
            if measurement.body_fat_percent is not None
            else (
                f"- Data: {measurement.created_at.date()}, "
                f"peso: {measurement.weight_kg} kg, "
                f"percentual de gordura: não informado"
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

    strategy = (
        current_strategy.strategy
        if current_strategy
        else "nenhuma estratégia cadastrada"
    )

    prompt = f"""
Você é um assistente de acompanhamento de progresso físico.

Analise os dados fornecidos de forma descritiva e cuidadosa.

Não faça diagnóstico médico.
Não recomende dietas restritivas.
Não gere metas calóricas.
Não gere metas personalizadas de macronutrientes.
Não trate estimativas de composição corporal como medidas exatas.

Objetivo do usuário:

{goal}

Frequência de exercícios:

{frequency}

Intensidade:

{intensity}

Estratégia atual:

{strategy}

Histórico de medições:

{measurements_text}

Determine se existem dados suficientes para avaliar a estratégia atual.

Responda EXATAMENTE em JSON, neste formato:

{{
    "should_reevaluate": true,
    "reason": "explicação objetiva baseada nos dados",
    "suggested_strategy": "nome ou descrição curta da estratégia que deveria ser avaliada"
}}

Regras:

- should_reevaluate deve ser true ou false.
- Se não houver dados suficientes, use false.
- suggested_strategy deve ser null quando should_reevaluate for false.
- Não invente dados que não foram fornecidos.
- A decisão deve ser baseada somente nas informações disponíveis.
"""

    try:
        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt
        )

        response_text = interaction.output_text

     
        result = json.loads(response_text)

        return {
            "should_reevaluate": bool(
                result.get("should_reevaluate", False)
            ),
            "reason": result.get(
                "reason",
                "A IA não forneceu uma justificativa."
            ),
            "suggested_strategy": result.get(
                "suggested_strategy"
            )
        }

    except Exception as error:
        raise error