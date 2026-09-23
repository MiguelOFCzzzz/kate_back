def calculate_nutrition_suggestion(
    weight_kg: float,
    height_cm: float,
    age: int,
    weekly_exercise_frequency: int,
    strategy: str
):
    if weight_kg <= 0:
        raise ValueError("Peso deve ser maior que zero.")

    if height_cm <= 0:
        raise ValueError("Altura deve ser maior que zero.")

    if age <= 0:
        raise ValueError("Idade deve ser maior que zero.")

    if weekly_exercise_frequency < 0:
        raise ValueError(
            "Frequência de exercícios não pode ser negativa."
        )

    if strategy not in {"recomp", "bulking", "cutting"}:
        raise ValueError(
            "Estratégia deve ser recomp, bulking ou cutting."
        )

    # Estimativa de metabolismo basal.
    # Usamos uma fórmula simples apenas para gerar
    # uma sugestão inicial que poderá ser revisada.
    bmr = (
        10 * weight_kg
        + 6.25 * height_cm
        - 5 * age
        + 5
    )

    activity_factors = {
        0: 1.2,
        1: 1.3,
        2: 1.35,
        3: 1.45,
        4: 1.5,
        5: 1.55,
        6: 1.6,
        7: 1.65
    }

    activity_factor = activity_factors.get(
        weekly_exercise_frequency,
        1.65
    )

    maintenance_calories = bmr * activity_factor

    if strategy == "bulking":
        daily_calories = maintenance_calories + 200
    elif strategy == "cutting":
        daily_calories = maintenance_calories - 200
    else:
        daily_calories = maintenance_calories

    protein_g = weight_kg * 1.6
    fats_g = weight_kg * 0.8

    calories_from_protein = protein_g * 4
    calories_from_fats = fats_g * 9

    remaining_calories = (
        daily_calories
        - calories_from_protein
        - calories_from_fats
    )

    carbohydrates_g = max(
        remaining_calories / 4,
        0
    )

    return {
        "strategy": strategy,
        "daily_calories": round(daily_calories),
        "protein_g": round(protein_g, 1),
        "carbohydrates_g": round(carbohydrates_g, 1),
        "fats_g": round(fats_g, 1)
    }