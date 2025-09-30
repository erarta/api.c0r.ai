"""
Personalized Nutrition Questionnaire System.
Collects comprehensive user preferences for maximum personalization of meal plans.
"""
from __future__ import annotations

from datetime import time, datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class QuestionType(str, Enum):
    """Types of questions in the questionnaire"""
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"
    TIME_PICKER = "time_picker"
    TEXT_INPUT = "text_input"
    YES_NO = "yes_no"
    SLIDER = "slider"


class Question(BaseModel):
    """Individual questionnaire question"""
    id: str
    type: QuestionType
    title: str
    description: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    placeholder: Optional[str] = None
    required: bool = True
    skip_logic: Optional[Dict[str, Any]] = None


class QuestionnaireStep(BaseModel):
    """Step in the questionnaire flow"""
    id: str
    title: str
    subtitle: Optional[str] = None
    icon: str
    questions: List[Question]
    completion_percentage: int


class UserResponse(BaseModel):
    """User's response to a question"""
    question_id: str
    value: Union[str, int, float, List[str], bool]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class NutritionPreferences(BaseModel):
    """Processed user preferences from questionnaire"""
    # Basic info
    goal: str
    daily_calories_target: Optional[int] = None
    activity_level: str

    # Dietary preferences
    dietary_restrictions: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    disliked_foods: List[str] = Field(default_factory=list)
    favorite_foods: List[str] = Field(default_factory=list)
    cuisines: List[str] = Field(default_factory=list)

    # Eating patterns
    meal_times: Dict[str, str] = Field(default_factory=dict)  # breakfast: "08:00"
    eating_frequency: str  # 3_meals, 5_small_meals, etc
    skip_meals: List[str] = Field(default_factory=list)

    # Lifestyle
    cooking_skill: str
    cooking_time_available: str
    work_schedule: str
    social_eating_frequency: str

    # Health considerations
    health_conditions: List[str] = Field(default_factory=list)
    supplements: List[str] = Field(default_factory=list)
    water_intake_goal: Optional[int] = None

    # Behavioral preferences
    meal_prep_preference: str
    snacking_preference: str
    weekend_eating_style: str
    stress_eating_tendency: int = Field(ge=1, le=5)  # 1-5 scale

    # Motivation and goals
    primary_motivation: str
    weight_goal: Optional[str] = None
    timeline: str
    accountability_preference: str


class NutritionQuestionnaire:
    """
    Comprehensive nutrition questionnaire system that adapts based on user responses
    and generates highly personalized meal plan preferences.
    """

    def __init__(self):
        self.questionnaire_steps = self._build_questionnaire()

    def _build_questionnaire(self) -> List[QuestionnaireStep]:
        """Build the complete questionnaire flow"""

        steps = []

        # Step 1: Welcome and Goals
        steps.append(QuestionnaireStep(
            id="goals_motivation",
            title="Ваши цели и мотивация",
            subtitle="Понимание ваших целей поможет создать идеальный план",
            icon="🎯",
            completion_percentage=10,
            questions=[
                Question(
                    id="primary_goal",
                    type=QuestionType.SINGLE_CHOICE,
                    title="Какая ваша основная цель в питании?",
                    options=[
                        {"value": "weight_loss", "label": "Снижение веса", "description": "Хочу похудеть и чувствовать себя легче"},
                        {"value": "muscle_gain", "label": "Набор мышечной массы", "description": "Стремлюсь увеличить мышцы и силу"},
                        {"value": "maintenance", "label": "Поддержание формы", "description": "Хочу оставаться в текущей форме"},
                        {"value": "health_improvement", "label": "Улучшение здоровья", "description": "Фокус на общем оздоровлении"},
                        {"value": "energy_boost", "label": "Больше энергии", "description": "Хочу чувствовать себя бодрее в течение дня"},
                        {"value": "digestive_health", "label": "Здоровье ЖКТ", "description": "Улучшить пищеварение и самочувствие"}
                    ]
                ),
                Question(
                    id="motivation_level",
                    type=QuestionType.SCALE,
                    title="Насколько сильно вы мотивированы изменить питание?",
                    min_value=1,
                    max_value=10,
                    description="1 - слабая мотивация, 10 - очень высокая"
                ),
                Question(
                    id="timeline",
                    type=QuestionType.SINGLE_CHOICE,
                    title="В какие сроки хотели бы видеть результаты?",
                    options=[
                        {"value": "1_month", "label": "1 месяц", "description": "Быстрые видимые изменения"},
                        {"value": "3_months", "label": "3 месяца", "description": "Устойчивые результаты"},
                        {"value": "6_months", "label": "6 месяцев", "description": "Кардинальная трансформация"},
                        {"value": "long_term", "label": "Долгосрочно", "description": "Образ жизни на всю жизнь"}
                    ]
                )
            ]
        ))

        # Step 2: Dietary Restrictions and Allergies
        steps.append(QuestionnaireStep(
            id="dietary_restrictions",
            title="Ограничения и предпочтения",
            subtitle="Расскажите о ваших особенностях питания",
            icon="🚫",
            completion_percentage=25,
            questions=[
                Question(
                    id="dietary_type",
                    type=QuestionType.MULTIPLE_CHOICE,
                    title="Следуете ли вы какой-то системе питания?",
                    options=[
                        {"value": "none", "label": "Никакой особой системы"},
                        {"value": "vegetarian", "label": "Вегетарианство"},
                        {"value": "vegan", "label": "Веганство"},
                        {"value": "pescatarian", "label": "Пескетарианство"},
                        {"value": "keto", "label": "Кето-диета"},
                        {"value": "paleo", "label": "Палео"},
                        {"value": "mediterranean", "label": "Средиземноморская"},
                        {"value": "intermittent_fasting", "label": "Интервальное голодание"},
                        {"value": "low_carb", "label": "Низкоуглеводная"},
                        {"value": "gluten_free", "label": "Безглютеновая"}
                    ]
                ),
                Question(
                    id="allergies",
                    type=QuestionType.MULTIPLE_CHOICE,
                    title="Есть ли у вас пищевые аллергии?",
                    options=[
                        {"value": "none", "label": "Нет аллергий"},
                        {"value": "nuts", "label": "Орехи"},
                        {"value": "shellfish", "label": "Морепродукты"},
                        {"value": "dairy", "label": "Молочные продукты"},
                        {"value": "eggs", "label": "Яйца"},
                        {"value": "gluten", "label": "Глютен"},
                        {"value": "soy", "label": "Соя"},
                        {"value": "fish", "label": "Рыба"},
                        {"value": "sesame", "label": "Кунжут"},
                        {"value": "other", "label": "Другие"}
                    ]
                ),
                Question(
                    id="dislikes",
                    type=QuestionType.MULTIPLE_CHOICE,
                    title="Что вы категорически не едите?",
                    description="Выберите продукты, которые не хотите видеть в плане",
                    options=[
                        {"value": "none", "label": "Ем все"},
                        {"value": "mushrooms", "label": "Грибы"},
                        {"value": "seafood", "label": "Морепродукты"},
                        {"value": "liver", "label": "Печень/субпродукты"},
                        {"value": "spicy", "label": "Острую пищу"},
                        {"value": "cilantro", "label": "Кинзу"},
                        {"value": "olives", "label": "Оливки"},
                        {"value": "tomatoes", "label": "Помидоры"},
                        {"value": "onions", "label": "Лук"},
                        {"value": "cottage_cheese", "label": "Творог"},
                        {"value": "avocado", "label": "Авокадо"}
                    ]
                )
            ]
        ))

        # Step 3: Food Preferences and Favorites
        steps.append(QuestionnaireStep(
            id="food_preferences",
            title="Ваши вкусы и предпочтения",
            subtitle="Что вы любите есть?",
            icon="😋",
            completion_percentage=40,
            questions=[
                Question(
                    id="favorite_cuisines",
                    type=QuestionType.MULTIPLE_CHOICE,
                    title="Какие кухни мира вам нравятся?",
                    options=[
                        {"value": "russian", "label": "Русская", "emoji": "🇷🇺"},
                        {"value": "italian", "label": "Итальянская", "emoji": "🇮🇹"},
                        {"value": "asian", "label": "Азиатская", "emoji": "🥢"},
                        {"value": "mediterranean", "label": "Средиземноморская", "emoji": "🫒"},
                        {"value": "mexican", "label": "Мексиканская", "emoji": "🌮"},
                        {"value": "indian", "label": "Индийская", "emoji": "🍛"},
                        {"value": "japanese", "label": "Японская", "emoji": "🍣"},
                        {"value": "georgian", "label": "Грузинская", "emoji": "🥟"},
                        {"value": "french", "label": "Французская", "emoji": "🇫🇷"},
                        {"value": "middle_eastern", "label": "Ближневосточная", "emoji": "🧆"}
                    ]
                ),
                Question(
                    id="favorite_proteins",
                    type=QuestionType.MULTIPLE_CHOICE,
                    title="Какие белки вы предпочитаете?",
                    options=[
                        {"value": "chicken", "label": "Курица", "emoji": "🐔"},
                        {"value": "beef", "label": "Говядина", "emoji": "🥩"},
                        {"value": "pork", "label": "Свинина", "emoji": "🐷"},
                        {"value": "fish", "label": "Рыба", "emoji": "🐟"},
                        {"value": "seafood", "label": "Морепродукты", "emoji": "🦐"},
                        {"value": "eggs", "label": "Яйца", "emoji": "🥚"},
                        {"value": "dairy", "label": "Молочные продукты", "emoji": "🧀"},
                        {"value": "legumes", "label": "Бобовые", "emoji": "🫘"},
                        {"value": "nuts_seeds", "label": "Орехи и семена", "emoji": "🥜"},
                        {"value": "tofu_tempeh", "label": "Тофу/темпе", "emoji": "🫛"}
                    ]
                ),
                Question(
                    id="carb_preferences",
                    type=QuestionType.MULTIPLE_CHOICE,
                    title="Какие углеводы вы любите?",
                    options=[
                        {"value": "rice", "label": "Рис", "emoji": "🍚"},
                        {"value": "pasta", "label": "Паста", "emoji": "🍝"},
                        {"value": "bread", "label": "Хлеб", "emoji": "🍞"},
                        {"value": "potatoes", "label": "Картофель", "emoji": "🥔"},
                        {"value": "quinoa", "label": "Киноа", "emoji": "🌾"},
                        {"value": "buckwheat", "label": "Гречка", "emoji": "🌾"},
                        {"value": "oats", "label": "Овсянка", "emoji": "🥣"},
                        {"value": "sweet_potato", "label": "Батат", "emoji": "🍠"},
                        {"value": "fruits", "label": "Фрукты", "emoji": "🍎"},
                        {"value": "vegetables", "label": "Овощи", "emoji": "🥕"}
                    ]
                )
            ]
        ))

        # Step 4: Eating Schedule and Patterns
        steps.append(QuestionnaireStep(
            id="eating_patterns",
            title="Ваш режим питания",
            subtitle="Когда и как часто вы едите?",
            icon="⏰",
            completion_percentage=55,
            questions=[
                Question(
                    id="breakfast_time",
                    type=QuestionType.TIME_PICKER,
                    title="Во сколько вы обычно завтракаете?",
                    description="Выберите привычное время или пропустите, если не завтракаете"
                ),
                Question(
                    id="lunch_time",
                    type=QuestionType.TIME_PICKER,
                    title="Во сколько обедаете?",
                    description="Ваше обычное время обеда"
                ),
                Question(
                    id="dinner_time",
                    type=QuestionType.TIME_PICKER,
                    title="Во сколько ужинаете?",
                    description="Привычное время ужина"
                ),
                Question(
                    id="eating_frequency",
                    type=QuestionType.SINGLE_CHOICE,
                    title="Как часто вы предпочитаете есть?",
                    options=[
                        {"value": "3_meals", "label": "3 основных приема пищи", "description": "Завтрак, обед, ужин"},
                        {"value": "5_small", "label": "5-6 небольших приемов", "description": "Частое питание малыми порциями"},
                        {"value": "2_meals", "label": "2 больших приема", "description": "Интервальное голодание или пропуск завтрака"},
                        {"value": "flexible", "label": "Гибкий график", "description": "По обстоятельствам и желанию"}
                    ]
                ),
                Question(
                    id="snacking_habits",
                    type=QuestionType.SINGLE_CHOICE,
                    title="Как относитесь к перекусам?",
                    options=[
                        {"value": "love_snacks", "label": "Обожаю перекусы", "description": "Не могу без них обходиться"},
                        {"value": "healthy_snacks", "label": "Только здоровые перекусы", "description": "Орехи, фрукты, йогурты"},
                        {"value": "minimal_snacks", "label": "Минимум перекусов", "description": "Только при сильном голоде"},
                        {"value": "no_snacks", "label": "Без перекусов", "description": "Предпочитаю основные приемы пищи"}
                    ]
                )
            ]
        ))

        # Step 5: Lifestyle and Cooking
        steps.append(QuestionnaireStep(
            id="lifestyle_cooking",
            title="Образ жизни и готовка",
            subtitle="Расскажите о своих возможностях",
            icon="👩‍🍳",
            completion_percentage=70,
            questions=[
                Question(
                    id="cooking_skill",
                    type=QuestionType.SINGLE_CHOICE,
                    title="Как оцениваете свои кулинарные навыки?",
                    options=[
                        {"value": "beginner", "label": "Начинающий", "description": "Простые блюда, минимум ингредиентов"},
                        {"value": "intermediate", "label": "Средний уровень", "description": "Умею готовить основные блюда"},
                        {"value": "advanced", "label": "Продвинутый", "description": "Люблю экспериментировать"},
                        {"value": "professional", "label": "Профессиональный", "description": "Готовка - мое хобби"}
                    ]
                ),
                Question(
                    id="cooking_time",
                    type=QuestionType.SINGLE_CHOICE,
                    title="Сколько времени готовы тратить на готовку в день?",
                    options=[
                        {"value": "minimal", "label": "10-20 минут", "description": "Быстрые и простые блюда"},
                        {"value": "moderate", "label": "30-45 минут", "description": "Умеренное время на готовку"},
                        {"value": "generous", "label": "1-1.5 часа", "description": "Люблю процесс готовки"},
                        {"value": "extensive", "label": "Более 1.5 часов", "description": "Готовка как хобби"}
                    ]
                ),
                Question(
                    id="meal_prep",
                    type=QuestionType.SINGLE_CHOICE,
                    title="Как относитесь к meal prep (заготовкам)?",
                    options=[
                        {"value": "love_prep", "label": "Обожаю готовить заранее", "description": "Воскресенье = день готовки"},
                        {"value": "some_prep", "label": "Иногда заготавливаю", "description": "Когда есть время и желание"},
                        {"value": "minimal_prep", "label": "Минимальные заготовки", "description": "Только нарезка овощей"},
                        {"value": "fresh_only", "label": "Только свежеприготовленное", "description": "Каждый раз готовлю новое"}
                    ]
                ),
                Question(
                    id="work_schedule",
                    type=QuestionType.SINGLE_CHOICE,
                    title="Какой у вас рабочий график?",
                    options=[
                        {"value": "office_9_5", "label": "Офис 9-18", "description": "Стандартный рабочий день"},
                        {"value": "remote_flexible", "label": "Удаленка с гибким графиком", "description": "Работаю из дома"},
                        {"value": "shift_work", "label": "Сменный график", "description": "Разное время работы"},
                        {"value": "irregular", "label": "Нерегулярный график", "description": "Фриланс, свободный график"},
                        {"value": "night_shift", "label": "Ночные смены", "description": "Работаю ночью"},
                        {"value": "student", "label": "Учеба", "description": "Студент/учащийся"}
                    ]
                )
            ]
        ))

        # Step 6: Health and Activity
        steps.append(QuestionnaireStep(
            id="health_activity",
            title="Здоровье и активность",
            subtitle="Особенности вашего здоровья и образа жизни",
            icon="🏃‍♀️",
            completion_percentage=85,
            questions=[
                Question(
                    id="activity_level",
                    type=QuestionType.SINGLE_CHOICE,
                    title="Какой у вас уровень физической активности?",
                    options=[
                        {"value": "sedentary", "label": "Сидячий образ жизни", "description": "Офисная работа, мало движения"},
                        {"value": "light", "label": "Легкая активность", "description": "Прогулки, легкие упражнения 1-3 раза в неделю"},
                        {"value": "moderate", "label": "Умеренная активность", "description": "Тренировки 3-5 раз в неделю"},
                        {"value": "high", "label": "Высокая активность", "description": "Интенсивные тренировки 6-7 раз в неделю"},
                        {"value": "athlete", "label": "Профессиональный спорт", "description": "Ежедневные интенсивные нагрузки"}
                    ]
                ),
                Question(
                    id="health_conditions",
                    type=QuestionType.MULTIPLE_CHOICE,
                    title="Есть ли у вас состояния здоровья, влияющие на питание?",
                    options=[
                        {"value": "none", "label": "Нет особенностей"},
                        {"value": "diabetes", "label": "Диабет"},
                        {"value": "hypertension", "label": "Повышенное давление"},
                        {"value": "cholesterol", "label": "Высокий холестерин"},
                        {"value": "ibs", "label": "СРК (синдром раздраженного кишечника)"},
                        {"value": "gerd", "label": "ГЭРБ (рефлюкс)"},
                        {"value": "thyroid", "label": "Заболевания щитовидной железы"},
                        {"value": "pcos", "label": "СПКЯ"},
                        {"value": "food_intolerances", "label": "Пищевые непереносимости"},
                        {"value": "other", "label": "Другие"}
                    ]
                ),
                Question(
                    id="stress_eating",
                    type=QuestionType.SCALE,
                    title="Склонны ли вы заедать стресс?",
                    min_value=1,
                    max_value=5,
                    description="1 - никогда не заедаю, 5 - очень часто заедаю стресс"
                ),
                Question(
                    id="water_intake",
                    type=QuestionType.SLIDER,
                    title="Сколько воды выпиваете в день? (стаканов)",
                    min_value=1,
                    max_value=15,
                    description="1 стакан = 250 мл"
                )
            ]
        ))

        # Step 7: Social and Weekend Patterns
        steps.append(QuestionnaireStep(
            id="social_patterns",
            title="Социальное питание",
            subtitle="Как проходят ваши выходные и встречи с друзьями?",
            icon="👥",
            completion_percentage=100,
            questions=[
                Question(
                    id="social_eating",
                    type=QuestionType.SINGLE_CHOICE,
                    title="Как часто едите в компании?",
                    options=[
                        {"value": "rarely", "label": "Редко", "description": "В основном ем один/одна"},
                        {"value": "sometimes", "label": "Иногда", "description": "1-2 раза в неделю"},
                        {"value": "often", "label": "Часто", "description": "3-4 раза в неделю"},
                        {"value": "always", "label": "Почти всегда", "description": "Предпочитаю есть в компании"}
                    ]
                ),
                Question(
                    id="weekend_eating",
                    type=QuestionType.SINGLE_CHOICE,
                    title="Как меняется ваше питание в выходные?",
                    options=[
                        {"value": "same", "label": "Никак не меняется", "description": "Тот же режим, что и в будни"},
                        {"value": "relaxed", "label": "Становится более свободным", "description": "Позже встаю, сдвигается режим"},
                        {"value": "indulgent", "label": "Позволяю себе вольности", "description": "Читмилы, рестораны, десерты"},
                        {"value": "meal_prep", "label": "Готовлю на неделю", "description": "Выходные для заготовок"}
                    ]
                ),
                Question(
                    id="budget_preference",
                    type=QuestionType.SINGLE_CHOICE,
                    title="Какой у вас бюджет на продукты?",
                    options=[
                        {"value": "economy", "label": "Экономный", "description": "Доступные продукты, разумная экономия"},
                        {"value": "moderate", "label": "Средний", "description": "Баланс цены и качества"},
                        {"value": "premium", "label": "Премиум", "description": "Качественные и дорогие продукты"},
                        {"value": "no_limit", "label": "Без ограничений", "description": "Цена не важна"}
                    ]
                ),
                Question(
                    id="motivation_support",
                    type=QuestionType.SINGLE_CHOICE,
                    title="Как вам лучше поддерживать мотивацию?",
                    options=[
                        {"value": "daily_tips", "label": "Ежедневные советы", "description": "Короткие полезные рекомендации"},
                        {"value": "progress_tracking", "label": "Отслеживание прогресса", "description": "Графики, метрики, достижения"},
                        {"value": "community", "label": "Поддержка сообщества", "description": "Общение с единомышленниками"},
                        {"value": "minimal", "label": "Минимальное вмешательство", "description": "Только план, без напоминаний"}
                    ]
                )
            ]
        ))

        return steps

    def get_questionnaire_flow(self, user_id: Optional[str] = None) -> List[QuestionnaireStep]:
        """Get complete questionnaire flow for user"""
        return self.questionnaire_steps

    def process_responses(self, responses: List[UserResponse]) -> NutritionPreferences:
        """Process user responses into structured preferences"""

        response_map = {resp.question_id: resp.value for resp in responses}

        # Process basic goals
        goal = response_map.get("primary_goal", "health_improvement")
        activity_level = response_map.get("activity_level", "moderate")
        timeline = response_map.get("timeline", "3_months")

        # Process dietary restrictions
        dietary_restrictions = []
        dietary_types = response_map.get("dietary_type", [])
        if isinstance(dietary_types, list):
            dietary_restrictions.extend([dt for dt in dietary_types if dt != "none"])

        allergies = response_map.get("allergies", [])
        if isinstance(allergies, list):
            allergies = [a for a in allergies if a != "none"]

        dislikes = response_map.get("dislikes", [])
        if isinstance(dislikes, list):
            dislikes = [d for d in dislikes if d != "none"]

        # Process food preferences
        cuisines = response_map.get("favorite_cuisines", [])
        favorite_proteins = response_map.get("favorite_proteins", [])
        favorite_carbs = response_map.get("carb_preferences", [])

        # Combine into favorites
        favorite_foods = []
        if isinstance(favorite_proteins, list):
            favorite_foods.extend(favorite_proteins)
        if isinstance(favorite_carbs, list):
            favorite_foods.extend(favorite_carbs)

        # Process meal times
        meal_times = {}
        for meal in ["breakfast", "lunch", "dinner"]:
            time_key = f"{meal}_time"
            if time_key in response_map and response_map[time_key]:
                meal_times[meal] = response_map[time_key]

        # Process eating patterns
        eating_frequency = response_map.get("eating_frequency", "3_meals")

        # Process lifestyle
        cooking_skill = response_map.get("cooking_skill", "intermediate")
        cooking_time_available = response_map.get("cooking_time", "moderate")
        work_schedule = response_map.get("work_schedule", "office_9_5")
        social_eating_frequency = response_map.get("social_eating", "sometimes")

        # Process health
        health_conditions = response_map.get("health_conditions", [])
        if isinstance(health_conditions, list):
            health_conditions = [hc for hc in health_conditions if hc != "none"]

        # Process behavioral patterns
        meal_prep_preference = response_map.get("meal_prep", "some_prep")
        snacking_preference = response_map.get("snacking_habits", "healthy_snacks")
        weekend_eating_style = response_map.get("weekend_eating", "relaxed")
        stress_eating_tendency = int(response_map.get("stress_eating", 3))

        # Process motivation
        primary_motivation = response_map.get("motivation_support", "progress_tracking")
        water_intake_goal = response_map.get("water_intake", 8)  # Default 8 glasses

        # Calculate daily calories target based on goal and activity
        daily_calories_target = self._calculate_calories_target(goal, activity_level, response_map)

        return NutritionPreferences(
            goal=goal,
            daily_calories_target=daily_calories_target,
            activity_level=activity_level,
            dietary_restrictions=dietary_restrictions,
            allergies=allergies,
            disliked_foods=dislikes,
            favorite_foods=favorite_foods,
            cuisines=cuisines,
            meal_times=meal_times,
            eating_frequency=eating_frequency,
            skip_meals=[],  # Will be determined from meal_times
            cooking_skill=cooking_skill,
            cooking_time_available=cooking_time_available,
            work_schedule=work_schedule,
            social_eating_frequency=social_eating_frequency,
            health_conditions=health_conditions,
            supplements=[],  # Can be added later
            water_intake_goal=water_intake_goal,
            meal_prep_preference=meal_prep_preference,
            snacking_preference=snacking_preference,
            weekend_eating_style=weekend_eating_style,
            stress_eating_tendency=stress_eating_tendency,
            primary_motivation=primary_motivation,
            weight_goal=goal if goal in ["weight_loss", "muscle_gain"] else None,
            timeline=timeline,
            accountability_preference=primary_motivation
        )

    def _calculate_calories_target(self, goal: str, activity_level: str, responses: Dict[str, Any]) -> Optional[int]:
        """Calculate daily calories target based on goal and activity level"""

        # Base calories by activity level (rough estimates)
        activity_multipliers = {
            "sedentary": 1800,
            "light": 2000,
            "moderate": 2200,
            "high": 2500,
            "athlete": 2800
        }

        base_calories = activity_multipliers.get(activity_level, 2000)

        # Adjust based on goal
        if goal == "weight_loss":
            return int(base_calories * 0.85)  # 15% deficit
        elif goal == "muscle_gain":
            return int(base_calories * 1.15)  # 15% surplus
        elif goal == "maintenance":
            return base_calories
        else:
            return base_calories  # Default for health/energy goals

    def generate_onboarding_summary(self, preferences: NutritionPreferences) -> str:
        """Generate a personalized summary of user preferences"""

        summary_parts = []

        # Goal summary
        goal_descriptions = {
            "weight_loss": "снижении веса",
            "muscle_gain": "наборе мышечной массы",
            "maintenance": "поддержании текущей формы",
            "health_improvement": "улучшении здоровья",
            "energy_boost": "повышении энергии",
            "digestive_health": "улучшении пищеварения"
        }

        goal_desc = goal_descriptions.get(preferences.goal, "достижении ваших целей")
        summary_parts.append(f"Ваша цель: {goal_desc}")

        # Dietary preferences
        if preferences.dietary_restrictions:
            restrictions_text = ", ".join(preferences.dietary_restrictions)
            summary_parts.append(f"Особенности питания: {restrictions_text}")

        if preferences.allergies:
            allergies_text = ", ".join(preferences.allergies)
            summary_parts.append(f"Аллергии: {allergies_text}")

        # Cooking preferences
        skill_descriptions = {
            "beginner": "простые рецепты",
            "intermediate": "рецепты средней сложности",
            "advanced": "разнообразные рецепты",
            "professional": "сложные кулинарные эксперименты"
        }

        skill_desc = skill_descriptions.get(preferences.cooking_skill, "подходящие рецепты")
        summary_parts.append(f"Уровень готовки: {skill_desc}")

        # Time preferences
        time_descriptions = {
            "minimal": "быстрые блюда (10-20 мин)",
            "moderate": "умеренное время готовки (30-45 мин)",
            "generous": "основательная готовка (до 1.5 часов)",
            "extensive": "кулинарное творчество (1.5+ часов)"
        }

        time_desc = time_descriptions.get(preferences.cooking_time_available, "подходящие по времени блюда")
        summary_parts.append(f"Время на готовку: {time_desc}")

        # Meal frequency
        freq_descriptions = {
            "3_meals": "3 основных приема пищи",
            "5_small": "5-6 небольших приемов пищи",
            "2_meals": "2 основных приема пищи",
            "flexible": "гибкий режим питания"
        }

        freq_desc = freq_descriptions.get(preferences.eating_frequency, "подходящий режим")
        summary_parts.append(f"Режим питания: {freq_desc}")

        # Activity level
        activity_descriptions = {
            "sedentary": "с учетом сидячего образа жизни",
            "light": "с легкими физическими нагрузками",
            "moderate": "с умеренными тренировками",
            "high": "с интенсивными тренировками",
            "athlete": "для профессиональных спортсменов"
        }

        activity_desc = activity_descriptions.get(preferences.activity_level, "под ваш образ жизни")
        summary_parts.append(f"Активность: {activity_desc}")

        # Calories target
        if preferences.daily_calories_target:
            summary_parts.append(f"Целевая калорийность: {preferences.daily_calories_target} ккал/день")

        return "Создам план питания " + ", ".join(summary_parts[:3]) + "."

    def get_adaptive_questions(self, current_responses: List[UserResponse]) -> List[Question]:
        """Get additional questions based on current responses for better personalization"""

        response_map = {resp.question_id: resp.value for resp in current_responses}
        adaptive_questions = []

        # If user has weight loss goal, ask about experience
        if response_map.get("primary_goal") == "weight_loss":
            adaptive_questions.append(
                Question(
                    id="weight_loss_experience",
                    type=QuestionType.SINGLE_CHOICE,
                    title="Есть ли опыт снижения веса?",
                    options=[
                        {"value": "first_time", "label": "Первый раз"},
                        {"value": "some_experience", "label": "Был опыт"},
                        {"value": "multiple_attempts", "label": "Много попыток"},
                        {"value": "yo_yo_dieting", "label": "Йо-йо эффект"}
                    ]
                )
            )

        # If user has health conditions, ask about medications
        health_conditions = response_map.get("health_conditions", [])
        if isinstance(health_conditions, list) and "none" not in health_conditions:
            adaptive_questions.append(
                Question(
                    id="medications_affecting_nutrition",
                    type=QuestionType.YES_NO,
                    title="Принимаете ли лекарства, влияющие на питание?",
                    description="Например, влияющие на аппетит или усвоение питательных веществ"
                )
            )

        # If user is very active, ask about training schedule
        if response_map.get("activity_level") in ["high", "athlete"]:
            adaptive_questions.append(
                Question(
                    id="training_schedule",
                    type=QuestionType.MULTIPLE_CHOICE,
                    title="В какие дни недели вы тренируетесь?",
                    options=[
                        {"value": "monday", "label": "Понедельник"},
                        {"value": "tuesday", "label": "Вторник"},
                        {"value": "wednesday", "label": "Среда"},
                        {"value": "thursday", "label": "Четверг"},
                        {"value": "friday", "label": "Пятница"},
                        {"value": "saturday", "label": "Суббота"},
                        {"value": "sunday", "label": "Воскресенье"}
                    ]
                )
            )

        return adaptive_questions