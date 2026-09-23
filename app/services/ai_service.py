import json

from google import genai

from app.config import settings


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


async def analyze_body_image(
    image_bytes: bytes,
    mime_type: str,
    user_goal: str | None = None,
    weekly_exercise_frequency: int | None = None
):
    prompt = f"""
Você é um assistente de análise visual para um aplicativo de nutrição e fitness.

Analise a imagem fornecida de forma cuidadosa.

Objetivo informado pelo usuário:
{user_goal}

Frequência semanal de exercícios:
{weekly_exercise_frequency}

A análise de composição corporal por imagem é apenas uma estimativa
aproximada e não substitui uma avaliação profissional.

Retorne APENAS um objeto JSON válido, sem markdown e sem texto antes ou depois.

Formato obrigatório:

{{
    "estimated_body_fat": null,
    "confidence": "baixa",
    "recommended_strategy": null,
    "reasoning": "",
    "limitations": ""
}}

Regras:
- estimated_body_fat deve ser um número aproximado ou null se não houver
  informação visual suficiente.
- confidence deve ser "baixa", "média" ou "alta".
- recommended_strategy pode ser "recomp", "bulking", "cutting" ou null.
- Não invente informações que não possam ser observadas ou inferidas
  razoavelmente.
- reasoning deve ser curto.
- limitations deve explicar as limitações da estimativa visual.
"""

    response = await client.aio.models.generate_content(
        model="gemini-3.6-flash",
        contents=[
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": image_bytes
                }
            },
            prompt
        ]
    )

    response_text = response.text.strip()

    try:
        return json.loads(response_text)

    except json.JSONDecodeError:
        if response_text.startswith("```json"):
            response_text = response_text[7:]

        if response_text.endswith("```"):
            response_text = response_text[:-3]

        return json.loads(response_text.strip())