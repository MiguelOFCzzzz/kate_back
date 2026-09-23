import json

from google import genai

from app.config import settings


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


async def analyze_meal_image(
    image_bytes: bytes,
    mime_type: str,
    ingredients: str | None = None,
    comment: str | None = None
):
    prompt = f"""
Você é um assistente de análise nutricional de refeições.

Analise a imagem fornecida e identifique os alimentos visíveis.

Informações adicionais fornecidas pelo usuário:

Ingredientes informados:
{ingredients or "Nenhum ingrediente informado."}

Comentário:
{comment or "Nenhum comentário informado."}

Use as informações fornecidas pelo usuário para complementar a análise
visual.

Se houver conflito entre a imagem e as informações fornecidas, considere
as informações explícitas do usuário como referência e indique a
incerteza quando necessário.

Para cada alimento identificado, estime:
- nome
- quantidade em gramas
- calorias
- proteínas
- carboidratos
- gorduras

Quando uma quantidade não puder ser determinada, faça uma estimativa
aproximada.

Retorne APENAS um objeto JSON válido, sem markdown e sem texto antes
ou depois.

Formato obrigatório:

{{
    "items": [
        {{
            "food_name": "",
            "estimated_weight_g": 0,
            "calories": 0,
            "protein_g": 0,
            "carbohydrates_g": 0,
            "fats_g": 0
        }}
    ],
    "total": {{
        "calories": 0,
        "protein_g": 0,
        "carbohydrates_g": 0,
        "fats_g": 0
    }},
    "confidence": "baixa",
    "limitations": ""
}}

Regras:
- confidence deve ser "baixa", "média" ou "alta".
- Os valores nutricionais são estimativas.
- Considere os ingredientes e comentários fornecidos pelo usuário.
- Não invente informações que contradigam informações explícitas.
- total deve corresponder aproximadamente à soma dos itens.
- limitations deve explicar as principais incertezas da análise.
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