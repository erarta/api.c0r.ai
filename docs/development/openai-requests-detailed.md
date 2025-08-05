# Детальное описание работы запросов OpenAI в c0r.ai

## 📁 Структура файлов

### Основные файлы:
- `services/ml/main.py` - Основная логика ML сервиса
- `services/ml/config.py` - Конфигурация моделей OpenAI
- `services/api/bot/handlers/photo.py` - Обработка фото в боте
- `shared/models/nutrition.py` - Модели данных для питания

## 🍽️ 1. Анализ еды (Food Analysis)

### 📍 Файл: `services/ml/main.py`

#### Функция: `analyze_food_with_openai()`
**Строки:** 67-285

```python
async def analyze_food_with_openai(image_bytes: bytes, user_language: str = "en", use_premium_model: bool = False) -> dict:
```

#### Конфигурация модели:
```python
# Из config.py
config = get_model_config("analysis", use_premium_model)
model = config["model"]           # "gpt-4o" или "gpt-4o-mini"
max_tokens = config["max_tokens"] # 500 для premium, 300 для standard
temperature = config["temperature"] # 0.1 для стабильности
```

#### Промпт для русского языка:
```python
prompt = """
Проанализируйте это изображение еды и предоставьте подробную информацию о питании.

ВАЖНО: Отвечайте ТОЛЬКО валидным JSON объектом без дополнительного текста.

Пожалуйста, предоставьте:
1. Список отдельных продуктов питания, видимых на изображении (используйте русские названия)
2. Оцененный вес/размер порции для каждого продукта в граммах
3. Калории для каждого отдельного продукта
4. Общую сводку по питанию

Верните ТОЛЬКО этот JSON объект:
{
    "food_items": [
        {
            "name": "русское название продукта (например: гречка, куриная грудка, помидор)",
            "weight": "вес в граммах (например: 100г, 150г)",
            "calories": число_калорий
        }
    ],
    "total_nutrition": {
        "calories": общее_число_калорий,
        "proteins": граммы_белков,
        "fats": граммы_жиров,
        "carbohydrates": граммы_углеводов
    }
}
"""
```

#### Промпт для английского языка:
```python
prompt = """
Analyze this food image and provide detailed nutritional information.

IMPORTANT: Respond with ONLY a valid JSON object, no additional text.

Please provide:
1. List of individual food items visible in the image (use specific food names)
2. Estimated weight/portion size for each item in grams
3. Calories for each individual item
4. Total nutritional summary

Return ONLY this JSON object:
{
    "food_items": [
        {
            "name": "specific food name (e.g., grilled chicken breast, brown rice, broccoli)",
            "weight": "weight in grams (e.g., 100g, 150g)",
            "calories": calorie_number
        }
    ],
    "total_nutrition": {
        "calories": total_calorie_number,
        "proteins": protein_grams,
        "fats": fat_grams,
        "carbohydrates": carb_grams
    }
}
"""
```

#### Запрос к OpenAI API:
```python
response = openai_client.chat.completions.create(
    model=model,                    # "gpt-4o" или "gpt-4o-mini"
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        }
    ],
    max_tokens=max_tokens,          # 500 для premium, 300 для standard
    temperature=temperature          # 0.1 для стабильности
)
```

#### Обработка ответа:
```python
# Парсинг JSON ответа
content = response.choices[0].message.content.strip()

# Очистка от markdown блоков
if content.startswith("```json"):
    content = content[7:-3].strip()
elif content.startswith("```"):
    content = content[3:-3].strip()

# Извлечение данных
response_data = json.loads(content)
kbzhu_data = response_data["total_nutrition"]

# Валидация обязательных полей
required_fields = ["calories", "proteins", "fats", "carbohydrates"]
for field in required_fields:
    kbzhu_data[field] = float(kbzhu_data[field])

# Возврат результата
result = {
    "kbzhu": kbzhu_data,
    "model_used": model,
    "food_items": response_data.get("food_items", [])
}
```

### 📍 Endpoint: `/api/v1/analyze`
**Строки:** 513-568

```python
@app.post(Routes.ML_ANALYZE)
@require_internal_auth
async def analyze_file(
    request: Request,
    photo: UploadFile = File(...),
    telegram_user_id: str = Form(...),
    provider: str = Form(default="openai"),
    user_language: str = Form(default="en"),
    use_premium_model: bool = Form(default=False)
):
```

## 🍳 2. Генерация рецептов (Recipe Generation)

### 📍 Функция: `generate_recipe_with_openai()`
**Строки:** 287-502

```python
async def generate_recipe_with_openai(image_url: str, user_context: dict, use_premium_model: bool = False) -> dict:
```

#### Конфигурация модели:
```python
config = get_model_config("recipe", use_premium_model)
model = config["model"]           # "gpt-4o" (всегда premium для рецептов)
max_tokens = config["max_tokens"] # 1000 для детальных рецептов
temperature = config["temperature"] # 0.3 для креативности
```

#### Построение персонализированного контекста:
```python
# Извлечение данных пользователя
user_language = user_context.get('language', 'en')
has_profile = user_context.get('has_profile', False)

# Сбор диетических предпочтений
context_parts = []
if has_profile:
    if user_context.get('dietary_preferences'):
        dietary_prefs = [pref for pref in user_context['dietary_preferences'] if pref != 'none']
        if dietary_prefs:
            context_parts.append(f"Dietary preferences: {', '.join(dietary_prefs)}")
    
    if user_context.get('allergies'):
        allergies = [allergy for allergy in user_context['allergies'] if allergy != 'none']
        if allergies:
            context_parts.append(f"Food allergies to avoid: {', '.join(allergies)}")
    
    if user_context.get('goal'):
        goal_map = {
            'lose_weight': 'weight loss',
            'maintain_weight': 'weight maintenance',
            'gain_weight': 'weight gain'
        }
        goal = goal_map.get(user_context['goal'], user_context['goal'])
        context_parts.append(f"Fitness goal: {goal}")
    
    if user_context.get('daily_calories_target'):
        context_parts.append(f"Daily calorie target: {user_context['daily_calories_target']} calories")

personal_context = "\n".join(context_parts) if context_parts else "No specific dietary requirements"
```

#### Промпт для русского языка:
```python
prompt = f"""
Проанализируйте это изображение еды/ингредиентов и создайте персонализированный рецепт.

ПЕРСОНАЛЬНЫЙ КОНТЕКСТ ПОЛЬЗОВАТЕЛЯ:
{personal_context}

Пожалуйста, создайте рецепт, который:
1. Использует ингредиенты, видимые на изображении
2. Соответствует диетическим предпочтениям пользователя
3. Избегает указанных аллергенов
4. Подходит для цели пользователя по фитнесу
5. Включает точную информацию о питании

Верните ТОЛЬКО JSON объект со следующей структурой:
{{
    "name": "название рецепта",
    "description": "краткое описание блюда",
    "prep_time": "время подготовки (например, 15 минут)",
    "cook_time": "время приготовления (например, 30 минут)",
    "servings": "количество порций (например, 4)",
    "ingredients": [
        "ингредиент 1 с количеством",
        "ингредиент 2 с количеством"
    ],
    "instructions": [
        "шаг 1 инструкции",
        "шаг 2 инструкции"
    ],
    "nutrition": {{
        "calories": число_калорий_на_порцию,
        "protein": число_белков_в_граммах,
        "carbs": число_углеводов_в_граммах,
        "fat": число_жиров_в_граммах
    }}
}}

Убедитесь, что рецепт безопасен и подходит для указанных диетических ограничений.
Все числовые значения должны быть числами (не строками).
"""
```

#### Промпт для английского языка:
```python
prompt = f"""
Analyze this food/ingredient image and create a personalized recipe.

USER'S PERSONAL CONTEXT:
{personal_context}

Please create a recipe that:
1. Uses the ingredients visible in the image
2. Matches the user's dietary preferences
3. Avoids specified allergens
4. Suits the user's fitness goal
5. Includes accurate nutritional information

Return ONLY a JSON object with the following structure:
{{
    "name": "recipe name",
    "description": "brief description of the dish",
    "prep_time": "preparation time (e.g., 15 minutes)",
    "cook_time": "cooking time (e.g., 30 minutes)",
    "servings": "number of servings (e.g., 4)",
    "ingredients": [
        "ingredient 1 with quantity",
        "ingredient 2 with quantity"
    ],
    "instructions": [
        "step 1 instruction",
        "step 2 instruction"
    ],
    "nutrition": {{
        "calories": calories_per_serving_number,
        "protein": protein_grams_number,
        "carbs": carbs_grams_number,
        "fat": fat_grams_number
    }}
}}

Ensure the recipe is safe and suitable for the specified dietary restrictions.
All numeric values should be numbers (not strings).
"""
```

#### Запрос к OpenAI API:
```python
response = openai_client.chat.completions.create(
    model=model,                    # "gpt-4o" для рецептов
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        }
    ],
    max_tokens=max_tokens,          # 1000 для детальных рецептов
    temperature=temperature          # 0.3 для креативности
)
```

#### Обработка ответа:
```python
# Парсинг JSON ответа
content = response.choices[0].message.content.strip()

# Очистка от markdown блоков
if content.startswith("```json"):
    content = content[7:-3]
elif content.startswith("```"):
    content = content[3:-3]

# Парсинг и валидация
recipe_data = json.loads(content)

# Проверка обязательных полей
required_fields = ["name", "ingredients", "instructions"]
for field in required_fields:
    if field not in recipe_data:
        raise ValueError(f"Missing field: {field}")

# Валидация данных о питании
if "nutrition" in recipe_data:
    nutrition = recipe_data["nutrition"]
    for nutrient in ["calories", "protein", "carbs", "fat"]:
        if nutrient in nutrition:
            nutrition[nutrient] = float(nutrition[nutrient])

return recipe_data
```

### 📍 Endpoint: `/api/v1/generate-recipe`
**Строки:** 569-604

```python
@app.post(Routes.ML_GENERATE_RECIPE)
@require_internal_auth
async def generate_recipe(
    request: Request,
    image_url: str = Form(...),
    telegram_user_id: str = Form(...),
    user_context: str = Form(...),
    use_premium_model: bool = Form(default=False)
):
```

## ⚙️ 3. Конфигурация моделей

### 📍 Файл: `services/ml/config.py`

#### Настройки по умолчанию:
```python
MODEL_CONFIGS = {
    "analysis": {
        "model": os.getenv("OPENAI_ANALYSIS_MODEL", "gpt-4o"),
        "max_tokens": int(os.getenv("OPENAI_ANALYSIS_MAX_TOKENS", "500")),
        "temperature": float(os.getenv("OPENAI_ANALYSIS_TEMPERATURE", "0.1")),
        "fallback_model": os.getenv("OPENAI_ANALYSIS_FALLBACK_MODEL", "gpt-4o-mini")
    },
    "recipe": {
        "model": os.getenv("OPENAI_RECIPE_MODEL", "gpt-4o"),
        "max_tokens": int(os.getenv("OPENAI_RECIPE_MAX_TOKENS", "1000")),
        "temperature": float(os.getenv("OPENAI_RECIPE_TEMPERATURE", "0.3")),
        "fallback_model": os.getenv("OPENAI_RECIPE_FALLBACK_MODEL", "gpt-4o-mini")
    }
}
```

#### Переменные окружения:
```bash
# Анализ еды
OPENAI_ANALYSIS_MODEL=gpt-4o
OPENAI_ANALYSIS_MAX_TOKENS=500
OPENAI_ANALYSIS_TEMPERATURE=0.1

# Генерация рецептов
OPENAI_RECIPE_MODEL=gpt-4o
OPENAI_RECIPE_MAX_TOKENS=1000
OPENAI_RECIPE_TEMPERATURE=0.3
```

## 🔄 4. Обработка в Telegram боте

### 📍 Файл: `services/api/bot/handlers/photo.py`

#### Обработка фото для анализа:
```python
async def process_nutrition_analysis(message: types.Message, state: FSMContext):
    # Загрузка фото
    photo = message.photo[-1]
    
    # Подготовка данных для ML сервиса
    files = {"photo": ("photo.jpg", photo_bytes, "image/jpeg")}
    data = {
        "telegram_user_id": str(telegram_user_id),
        "provider": "openai",
        "user_language": user_language,
        "use_premium_model": False  # Можно изменить на True для премиум
    }
    
    # Вызов ML сервиса
    response = await client.post(
        f"{ML_SERVICE_URL}/api/v1/analyze",
        files=files,
        data=data,
        headers=auth_headers,
        timeout=60.0
    )
```

## 📊 5. Модели данных

### 📍 Файл: `shared/models/nutrition.py`

#### Модель ответа анализа:
```python
class AnalysisResponse(BaseResponse):
    """Response model for food analysis"""
    kbzhu: NutritionData = Field(..., description="Total nutritional information (KBZHU)")
    food_items: Optional[List[FoodItem]] = Field(None, description="Individual food items breakdown")
    analysis_provider: str = Field(default="openai", description="AI provider used for analysis")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="Analysis confidence (0-1)")
```

## 🎯 6. Ключевые особенности

### Анализ еды:
- ✅ **Стабильность**: Temperature 0.1 для консистентных результатов
- ✅ **Точность**: Валидация всех числовых значений
- ✅ **Fallback**: Автоматический переход на Gemini при ошибке
- ✅ **Двуязычность**: Поддержка русского и английского

### Генерация рецептов:
- ✅ **Креативность**: Temperature 0.3 для разнообразных рецептов
- ✅ **Персонализация**: Учет диетических предпочтений и аллергий
- ✅ **Детальность**: 1000 токенов для подробных инструкций
- ✅ **Безопасность**: Проверка на аллергены и ограничения

### Конфигурация:
- ✅ **Гибкость**: Настройка через переменные окружения
- ✅ **Масштабируемость**: Разные модели для разных задач
- ✅ **Мониторинг**: Логирование используемых моделей
- ✅ **Fallback**: Резервные модели при ошибках 