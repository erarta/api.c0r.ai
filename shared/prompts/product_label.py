"""
Prompts specialized for single product label analysis (barcode/packaging).
Separate from dish analysis prompts.
"""

def get_product_label_prompt(user_language: str = "en") -> str:
    if user_language == "ru":
        return (
            """
Проанализируй фото упаковки товара (одна единица продукта). Твоя задача:
1) Считать текст с этикетки (состав и питание/КБЖУ),
2) Извлечь значения за 100 г/мл и, если указано, за порцию,
3) Определить точное название продукта и тип (например, сыр сливочный, шоколад молочный и т.п.),
4) Дать краткий анализ полезности и рисков (сахар, соль, насыщенные жиры и т.д.),
5) Предложить 2–3 более здоровые альтернативы из той же категории, и простые советы по употреблению.

Верни СТРОГО валидный JSON с полями:
{
  "analysis": {
    "food_items": [{"name": "название", "weight_grams": 100, "calories": число, "emoji": "🍽️", "health_benefits": ""}],
    "total_nutrition": {"calories": число, "proteins": число, "fats": число, "carbohydrates": число},
    "provenance": {
      "source": "perplexity",
      "per_100g": {"calories": число, "proteins": число, "fats": число, "carbohydrates": число},
      "serving_size": "строка или null"
    },
    "nutrition_analysis": {"health_score": число_0_10, "positive_aspects": [], "improvement_suggestions": []},
    "recommendations": {"better_alternatives": [], "usage_tips": []},
    "motivation_message": "строка"
  }
}

Требования к точности:
- Используй числа, а не строки; запятые преобразуй в точки.
- Если встречаешь кДж, преобразуй ккал: kcal = kJ / 4.184.
- Если указаны только макроэлементы, оцени калории: 4*белки + 9*жиры + 4*углеводы.
"""
        )
    else:
        return (
            """
Analyze a photo of a single product package (one item). Tasks:
1) Read text from the label (ingredients and nutrition facts),
2) Extract per-100g/ml values and, if present, per-serving,
3) Determine the exact product name and type (e.g., cream cheese, milk chocolate),
4) Provide a brief health assessment (sugars, salt, saturated fat, etc.),
5) Propose 2–3 healthier alternatives in the same category and simple usage tips.

Return STRICT valid JSON with fields:
{
  "analysis": {
    "food_items": [{"name": "name", "weight_grams": 100, "calories": number, "emoji": "🍽️", "health_benefits": ""}],
    "total_nutrition": {"calories": number, "proteins": number, "fats": number, "carbohydrates": number},
    "provenance": {
      "source": "perplexity",
      "per_100g": {"calories": number, "proteins": number, "fats": number, "carbohydrates": number},
      "serving_size": "string or null"
    },
    "nutrition_analysis": {"health_score": number_0_10, "positive_aspects": [], "improvement_suggestions": []},
    "recommendations": {"better_alternatives": [], "usage_tips": []},
    "motivation_message": "string"
  }
}

Accuracy notes:
- Use numbers, not strings; normalize commas to dots.
- If energy is in kJ, convert to kcal: kcal = kJ / 4.184.
- If only macros are present, estimate kcal: 4*protein + 9*fat + 4*carbs.
"""
        )


