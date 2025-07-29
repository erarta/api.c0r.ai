# Архитектура улучшенных промптов для анализа еды и генерации рецептов

## Обзор

Новая система промптов обеспечивает региональную адаптацию, мотивационные элементы, объяснение пользы продуктов и генерацию 3 ранжированных рецептов с максимальной точностью определения веса порций.

## Архитектура системы промптов

### Структура модулей

```
services/ml/core/prompts/
├── base/                    # Базовые шаблоны
│   ├── templates.py         # Основные шаблоны промптов
│   └── validators.py        # Валидация промптов
├── food_analysis/           # Промпты для анализа еды
│   ├── enhanced_analysis.py # Улучшенный анализ с мотивацией
│   ├── regional_adaptation.py # Региональная адаптация
│   └── nutrition_benefits.py # Объяснение пользы продуктов
├── recipe_generation/       # Промпты для рецептов
│   ├── triple_recipe_generator.py # Генерация 3 рецептов
│   ├── recipe_ranker.py     # Ранжирование рецептов
│   └── regional_recipes.py  # Региональные рецепты
├── motivation/              # Мотивационная система
│   ├── praise_system.py     # Система похвалы
│   └── encouragement.py     # Поощрения
└── utils/
    ├── prompt_builder.py    # Конструктор промптов
    └── context_manager.py   # Управление контекстом
```

## Базовая архитектура промптов

### PromptTemplate

```python
@dataclass
class PromptTemplate:
    """Базовый шаблон промпта"""
    name: str
    language: str
    region: str
    template: str
    variables: Dict[str, Any]
    validation_rules: List[str]
    expected_output_format: str
```

### PromptBuilder

```python
class PromptBuilder:
    """Конструктор промптов с поддержкой региональной адаптации"""
    
    def __init__(self):
        self.regional_data = RegionalDataManager()
        self.motivation_system = MotivationSystem()
        self.nutrition_explainer = NutritionBenefitsExplainer()
    
    def build_food_analysis_prompt(self, 
                                 user_language: str,
                                 regional_context: RegionalContext,
                                 user_profile: dict,
                                 motivation_level: str = "standard") -> str:
        """Создает улучшенный промпт для анализа еды"""
        
    def build_recipe_generation_prompt(self,
                                     user_language: str,
                                     regional_context: RegionalContext,
                                     user_profile: dict,
                                     recipe_count: int = 3) -> str:
        """Создает промпт для генерации множественных рецептов"""
```

## Улучшенные промпты для анализа еды

### Структура промпта с региональной адаптацией

```python
ENHANCED_FOOD_ANALYSIS_TEMPLATE = """
{motivation_greeting}

Проанализируй это изображение еды как эксперт по питанию, специализирующийся на {regional_cuisine} кухне.

РЕГИОНАЛЬНЫЙ КОНТЕКСТ:
- Регион: {region_name}
- Типичные продукты: {common_regional_products}
- Сезонные особенности: {seasonal_context}
- Единицы измерения: {measurement_units}

ЗАДАЧА АНАЛИЗА:
1. Определи все продукты на изображении, уделяя особое внимание {regional_products_emphasis}
2. Оцени вес каждого продукта с учетом {portion_size_context}
3. Рассчитай точную пищевую ценность
4. Объясни пользу каждого продукта для здоровья
5. Добавь мотивационное сообщение о важности отслеживания питания

ФОРМАТ ОТВЕТА (строго JSON):
{{
    "motivation_message": "{{персональное поздравление за ведение учета питания}}",
    "food_items": [
        {{
            "name": "{{точное название продукта на {language}}}",
            "regional_name": "{{местное/традиционное название если отличается}}",
            "weight_grams": {{точный вес в граммах}},
            "weight_confidence": {{уверенность в оценке веса 0-1}},
            "calories": {{калории}},
            "proteins": {{белки в граммах}},
            "fats": {{жиры в граммах}},
            "carbohydrates": {{углеводы в граммах}},
            "health_benefits": "{{объяснение пользы этого продукта}}",
            "regional_significance": "{{значение в местной кухне}}"
        }}
    ],
    "total_nutrition": {{
        "calories": {{общие калории}},
        "proteins": {{общие белки}},
        "fats": {{общие жиры}},
        "carbohydrates": {{общие углеводы}},
        "estimated_plate_weight": {{оценка веса всей тарелки в граммах}}
    }},
    "nutritional_analysis": {{
        "overall_healthiness": "{{оценка полезности блюда}}",
        "dietary_recommendations": "{{рекомендации по питанию}}",
        "regional_nutrition_notes": "{{особенности питательности в контексте региональной кухни}}"
    }},
    "encouragement": "{{мотивационное сообщение о важности здорового питания}}"
}}

{detailed_analysis_instructions}

{motivation_footer}
"""
```

### Мотивационная система

```python
class MotivationSystem:
    """Система мотивации и поощрения пользователей"""
    
    MOTIVATION_LEVELS = {
        "beginner": "новичок в отслеживании питания",
        "regular": "регулярно отслеживает питание", 
        "advanced": "опытный в вопросах питания"
    }
    
    def get_motivation_greeting(self, 
                              user_language: str,
                              user_level: str,
                              analysis_count: int) -> str:
        """Генерирует персональное приветствие"""
        
    def get_encouragement_message(self,
                                user_language: str,
                                nutritional_quality: str) -> str:
        """Генерирует поощрительное сообщение"""
```

### Региональная адаптация промптов

```python
REGIONAL_ANALYSIS_ADAPTATIONS = {
    "RU": {
        "greeting": "Привет! Отлично, что ты следишь за своим питанием! 🌟",
        "product_emphasis": "русские и традиционные продукты (гречка, творог, ряженка, квашеная капуста)",
        "portion_context": "стандартные российские порции и посуда",
        "measurement_focus": "граммы и миллилитры",
        "cultural_notes": "учитывая особенности русской кухни и пищевых привычек",
        "seasonal_awareness": "с учетом сезонности продуктов в России",
        "encouragement": "Ты делаешь важный шаг к здоровому образу жизни! Каждый анализ приближает тебя к цели! 💪"
    },
    "US": {
        "greeting": "Great job tracking your nutrition! 🌟",
        "product_emphasis": "American and international foods",
        "portion_context": "standard US portion sizes and dishware",
        "measurement_focus": "grams with imperial equivalents",
        "cultural_notes": "considering American dietary patterns",
        "seasonal_awareness": "accounting for seasonal availability in the US",
        "encouragement": "You're making excellent progress on your health journey! Keep it up! 💪"
    }
}
```

## Система генерации 3 рецептов

### Архитектура тройной генерации

```python
class TripleRecipeGenerator:
    """Генератор трех ранжированных рецептов"""
    
    async def generate_three_ranked_recipes(self,
                                          image_url: str,
                                          user_context: dict,
                                          regional_context: RegionalContext) -> List[RankedRecipe]:
        """
        Генерирует 3 рецепта с разными подходами:
        1. Максимально подходящий пользователю
        2. Традиционный региональный
        3. Креативный/современный вариант
        """
```

### Промпт для генерации 3 рецептов

```python
TRIPLE_RECIPE_GENERATION_TEMPLATE = """
{motivation_greeting}

Ты - шеф-повар и эксперт по {regional_cuisine} кухне. Проанализируй изображение и создай ТРИ разных рецепта.

КОНТЕКСТ ПОЛЬЗОВАТЕЛЯ:
- Регион: {region}
- Диетические предпочтения: {dietary_preferences}
- Аллергии: {allergies}
- Цель: {fitness_goal}
- Уровень готовки: {cooking_skill}
- Доступное время: {available_time}

ТРЕБОВАНИЯ К РЕЦЕПТАМ:
1. ПЕРСОНАЛЬНЫЙ РЕЦЕПТ - максимально подходящий профилю пользователя
2. ТРАДИЦИОННЫЙ РЕЦЕПТ - классический {regional_cuisine} рецепт
3. КРЕАТИВНЫЙ РЕЦЕПТ - современная интерпретация или фьюжн

Каждый рецепт должен:
- Использовать ингредиенты с фото
- Быть адаптированным под {region}
- Учитывать доступность продуктов
- Соответствовать цели {fitness_goal}

ФОРМАТ ОТВЕТА (строго JSON):
{{
    "motivation_message": "{{поздравление за желание готовить здоровую еду}}",
    "recipes": [
        {{
            "rank": 1,
            "type": "personal",
            "suitability_score": {{0-100}},
            "name": "{{название рецепта}}",
            "description": "{{почему этот рецепт идеален для пользователя}}",
            "prep_time": "{{время подготовки}}",
            "cook_time": "{{время готовки}}",
            "difficulty": "{{easy/medium/hard}}",
            "servings": {{количество порций}},
            "ingredients": [
                {{
                    "item": "{{ингредиент}}",
                    "amount": "{{количество}}",
                    "regional_availability": "{{легко найти/сезонный/редкий}}"
                }}
            ],
            "instructions": [
                "{{пошаговая инструкция}}"
            ],
            "nutrition_per_serving": {{
                "calories": {{калории}},
                "protein": {{белки}},
                "carbs": {{углеводы}},
                "fat": {{жиры}}
            }},
            "health_benefits": "{{польза блюда для здоровья}}",
            "regional_notes": "{{особенности приготовления в {region}}}",
            "personalization_notes": "{{почему подходит именно этому пользователю}}"
        }},
        {{
            "rank": 2,
            "type": "traditional",
            "suitability_score": {{0-100}},
            // ... аналогичная структура для традиционного рецепта
        }},
        {{
            "rank": 3,
            "type": "creative",
            "suitability_score": {{0-100}},
            // ... аналогичная структура для креативного рецепта
        }}
    ],
    "ingredient_analysis": {{
        "recognized_ingredients": [{{список распознанных ингредиентов}}],
        "suggested_additions": [{{предложения дополнительных ингредиентов}}],
        "regional_substitutes": {{{{маппинг замен для региона}}}}
    }},
    "cooking_tips": [
        "{{советы по готовке для {region}}}"
    ],
    "encouragement": "{{мотивация к здоровому питанию и готовке}}"
}}

{detailed_recipe_instructions}

{motivation_footer}
"""
```

### Система ранжирования рецептов

```python
class RecipeRanker:
    """Система ранжирования рецептов по соответствию пользователю"""
    
    def calculate_suitability_score(self,
                                  recipe: dict,
                                  user_profile: dict,
                                  regional_context: RegionalContext) -> float:
        """
        Рассчитывает оценку соответствия рецепта пользователю
        
        Факторы оценки:
        - Соответствие диетическим предпочтениям (30%)
        - Отсутствие аллергенов (25%)
        - Соответствие фитнес-целям (20%)
        - Доступность ингредиентов в регионе (15%)
        - Сложность приготовления (10%)
        """
        
    def rank_recipes(self, recipes: List[dict], user_profile: dict) -> List[RankedRecipe]:
        """Ранжирует рецепты по убыванию соответствия"""
```

## Система объяснения пользы продуктов

### NutritionBenefitsExplainer

```python
class NutritionBenefitsExplainer:
    """Система объяснения пользы продуктов для здоровья"""
    
    def __init__(self):
        self.nutrition_database = NutritionDatabase()
        self.regional_benefits = RegionalNutritionBenefits()
    
    def explain_food_benefits(self,
                            food_item: str,
                            user_language: str,
                            regional_context: RegionalContext) -> str:
        """
        Объясняет пользу конкретного продукта
        
        Включает:
        - Основные питательные вещества
        - Влияние на здоровье
        - Роль в региональной диете
        - Сезонные особенности
        """
        
    def generate_overall_meal_benefits(self,
                                     food_items: List[dict],
                                     user_language: str) -> str:
        """Анализирует общую пользу всего блюда"""
```

### База знаний о пользе продуктов

```python
NUTRITION_BENEFITS_DATABASE = {
    "гречка": {
        "ru": {
            "main_benefits": "Богата белком, железом и магнием",
            "health_impact": "Поддерживает сердечно-сосудистую систему, нормализует уровень сахара",
            "regional_significance": "Традиционный русский суперфуд, основа здорового питания",
            "seasonal_notes": "Особенно полезна зимой для поддержания энергии"
        },
        "en": {
            "main_benefits": "Rich in protein, iron, and magnesium",
            "health_impact": "Supports cardiovascular health, regulates blood sugar",
            "regional_significance": "Traditional Russian superfood, foundation of healthy eating",
            "seasonal_notes": "Especially beneficial in winter for energy maintenance"
        }
    }
    // ... база для всех продуктов
}
```

## Точная оценка веса тарелки

### Алгоритм оценки веса

```python
class PlateWeightEstimator:
    """Система точной оценки веса порций"""
    
    def __init__(self):
        self.portion_standards = PortionStandards()
        self.visual_analysis = VisualPortionAnalyzer()
    
    def estimate_portion_weights(self,
                               food_items: List[str],
                               visual_cues: dict,
                               regional_context: RegionalContext) -> Dict[str, float]:
        """
        Оценивает вес каждого продукта на основе:
        - Визуального анализа размеров
        - Стандартных порций для региона
        - Соотношения продуктов на тарелке
        - Типа посуды (если определяется)
        """
```

### Промпт для точной оценки веса

```python
WEIGHT_ESTIMATION_INSTRUCTIONS = """
ТОЧНАЯ ОЦЕНКА ВЕСА ПОРЦИЙ:

1. Анализируй размер тарелки/посуды как референс
2. Сравнивай продукты между собой по объему
3. Используй стандартные порции для {region}:
   {regional_portion_standards}

4. Учитывай плотность продуктов:
   - Жидкости: объем = вес
   - Крупы: коэффициент плотности ~0.8
   - Овощи: коэффициент плотности ~0.9
   - Мясо: коэффициент плотности ~1.0

5. Оценивай уверенность в каждой оценке (0-1)
6. Если видна рука/столовые приборы - используй как масштаб

СТАНДАРТНЫЕ ПОРЦИИ ДЛЯ {region}:
{portion_size_guide}
"""
```

## Конфигурация промптов

### Настройки для разных моделей

```python
PROMPT_CONFIGS = {
    "gpt-4o": {
        "max_context_length": 128000,
        "optimal_prompt_length": 4000,
        "supports_detailed_instructions": True,
        "json_reliability": 0.95,
        "creativity_level": "high"
    },
    "gpt-4o-mini": {
        "max_context_length": 128000,
        "optimal_prompt_length": 2000,
        "supports_detailed_instructions": True,
        "json_reliability": 0.90,
        "creativity_level": "medium"
    }
}
```

### Адаптация промптов под модель

```python
class ModelPromptAdapter:
    """Адаптер промптов под конкретные модели"""
    
    def adapt_prompt_for_model(self,
                             base_prompt: str,
                             model_name: str,
                             task_type: str) -> str:
        """
        Адаптирует промпт под возможности конкретной модели
        - Сокращает для моделей с ограничениями
        - Добавляет специфичные инструкции
        - Оптимизирует для лучшего качества ответа
        """
```

## Система валидации промптов

### PromptValidator

```python
class PromptValidator:
    """Валидатор промптов и их результатов"""
    
    def validate_prompt_structure(self, prompt: str) -> ValidationResult:
        """Проверяет структуру промпта"""
        
    def validate_expected_output(self, 
                               response: str,
                               expected_format: str) -> ValidationResult:
        """Проверяет соответствие ответа ожидаемому формату"""
        
    def suggest_prompt_improvements(self, 
                                  prompt: str,
                                  model_name: str) -> List[str]:
        """Предлагает улучшения промпта"""
```

## Мониторинг качества промптов

### Метрики качества

```python
PROMPT_QUALITY_METRICS = {
    "json_parse_success_rate": "процент успешного парсинга JSON",
    "field_completeness": "полнота заполнения полей",
    "regional_accuracy": "точность региональной адаптации",
    "motivation_effectiveness": "эффективность мотивационных элементов",
    "weight_estimation_accuracy": "точность оценки веса",
    "recipe_relevance_score": "релевантность рецептов пользователю"
}
```

### A/B тестирование промптов

```python
class PromptABTester:
    """Система A/B тестирования промптов"""
    
    async def run_prompt_comparison(self,
                                  prompt_a: str,
                                  prompt_b: str,
                                  test_images: List[str],
                                  evaluation_criteria: List[str]) -> ComparisonResult:
        """Сравнивает эффективность двух промптов"""
```

## Заключение

Новая архитектура промптов обеспечивает:

1. **Региональную адаптацию** - точное распознавание местных продуктов
2. **Мотивационную систему** - поощрение здоровых привычек
3. **Тройную генерацию рецептов** - максимальный выбор для пользователя
4. **Точную оценку веса** - улучшенная точность подсчета калорий
5. **Объяснение пользы** - образовательная ценность каждого анализа
6. **Масштабируемость** - легкое добавление новых регионов и языков

Система построена с учетом лучших практик prompt engineering и обеспечивает максимальное качество анализа еды и генерации рецептов.