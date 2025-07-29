"""
Nutrition Benefits Explanation System for c0r.AI ML Service
Provides detailed health benefits explanations for food products
"""

from typing import Dict, List, Optional, Tuple
from loguru import logger


class NutritionBenefitsExplainer:
    """Система объяснения пользы продуктов для здоровья"""
    
    def __init__(self):
        self.benefits_database = self._load_benefits_database()
        self.nutrient_functions = self._load_nutrient_functions()
        self.health_conditions_map = self._load_health_conditions_map()
        
        logger.info("💚 NutritionBenefitsExplainer initialized")
    
    def explain_food_benefits(self, 
                            food_name: str, 
                            language: str = "ru",
                            user_goals: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Объяснение пользы конкретного продукта
        
        Args:
            food_name: Название продукта
            language: Язык объяснения
            user_goals: Цели пользователя (похудение, набор массы и т.д.)
            
        Returns:
            Словарь с объяснениями пользы
        """
        logger.debug(f"💡 Explaining benefits for {food_name} in {language}")
        
        food_lower = food_name.lower()
        benefits = {}
        
        # Поиск продукта в базе данных
        product_benefits = self._find_product_benefits(food_lower, language)
        
        if product_benefits:
            benefits.update(product_benefits)
        
        # Добавляем персонализированные советы на основе целей
        if user_goals:
            personalized_benefits = self._get_personalized_benefits(
                food_lower, user_goals, language
            )
            if personalized_benefits:
                benefits["personalized_advice"] = personalized_benefits
        
        # Если не найдено специфических данных, используем общие принципы
        if not benefits:
            benefits = self._get_general_benefits(food_lower, language)
        
        return benefits
    
    def explain_nutrient_benefits(self, 
                                nutrient_name: str, 
                                amount: float,
                                language: str = "ru") -> str:
        """
        Объяснение пользы конкретного нутриента
        
        Args:
            nutrient_name: Название нутриента
            amount: Количество в граммах/мг
            language: Язык объяснения
            
        Returns:
            Объяснение пользы нутриента
        """
        logger.debug(f"🧬 Explaining nutrient {nutrient_name}: {amount}")
        
        nutrient_data = self.nutrient_functions.get(nutrient_name.lower(), {})
        
        if not nutrient_data:
            return self._get_default_nutrient_explanation(nutrient_name, language)
        
        explanation_template = nutrient_data.get(language, nutrient_data.get("en", ""))
        
        # Добавляем информацию о количестве
        amount_context = self._get_amount_context(nutrient_name, amount, language)
        
        return f"{explanation_template} {amount_context}"
    
    def get_meal_balance_advice(self, 
                              nutrition_data: Dict[str, float],
                              language: str = "ru") -> str:
        """
        Советы по сбалансированности блюда
        
        Args:
            nutrition_data: Данные о питательности (белки, жиры, углеводы)
            language: Язык советов
            
        Returns:
            Советы по балансу питания
        """
        logger.debug("⚖️ Analyzing meal balance")
        
        proteins = nutrition_data.get("proteins", 0)
        fats = nutrition_data.get("fats", 0)
        carbs = nutrition_data.get("carbohydrates", 0)
        calories = nutrition_data.get("calories", 0)
        
        if calories == 0:
            return "Недостаточно данных для анализа" if language == "ru" else "Insufficient data for analysis"
        
        # Рассчитываем процентное соотношение БЖУ
        protein_percent = (proteins * 4 / calories) * 100
        fat_percent = (fats * 9 / calories) * 100
        carb_percent = (carbs * 4 / calories) * 100
        
        advice_parts = []
        
        # Анализ белков
        if protein_percent < 15:
            if language == "ru":
                advice_parts.append("🥩 Рекомендуется добавить больше белковых продуктов для лучшего насыщения")
            else:
                advice_parts.append("🥩 Consider adding more protein sources for better satiety")
        elif protein_percent > 35:
            if language == "ru":
                advice_parts.append("⚖️ Много белка - отлично для мышц, но следите за балансом")
            else:
                advice_parts.append("⚖️ High protein content - great for muscles, but watch the balance")
        
        # Анализ жиров
        if fat_percent < 20:
            if language == "ru":
                advice_parts.append("🥑 Полезные жиры помогут усвоению витаминов")
            else:
                advice_parts.append("🥑 Healthy fats would help vitamin absorption")
        elif fat_percent > 40:
            if language == "ru":
                advice_parts.append("🔥 Высокое содержание жиров - следите за общей калорийностью")
            else:
                advice_parts.append("🔥 High fat content - monitor total calorie intake")
        
        # Анализ углеводов
        if carb_percent < 30:
            if language == "ru":
                advice_parts.append("⚡ Углеводы дадут энергию для активности")
            else:
                advice_parts.append("⚡ Carbohydrates would provide energy for activity")
        elif carb_percent > 60:
            if language == "ru":
                advice_parts.append("🌾 Много углеводов - хорошо для энергии, но следите за сахаром")
            else:
                advice_parts.append("🌾 High carb content - good for energy, but watch sugar levels")
        
        # Общая оценка баланса
        if 15 <= protein_percent <= 25 and 25 <= fat_percent <= 35 and 40 <= carb_percent <= 55:
            if language == "ru":
                advice_parts.insert(0, "✅ Отлично сбалансированное блюдо!")
            else:
                advice_parts.insert(0, "✅ Excellently balanced meal!")
        
        return " ".join(advice_parts) if advice_parts else (
            "Хорошо сбалансированное блюдо" if language == "ru" else "Well-balanced meal"
        )
    
    def get_seasonal_benefits(self, 
                            food_name: str, 
                            season: str,
                            language: str = "ru") -> Optional[str]:
        """
        Получение информации о сезонной пользе продукта
        
        Args:
            food_name: Название продукта
            season: Сезон (spring, summer, autumn, winter)
            language: Язык
            
        Returns:
            Информация о сезонной пользе
        """
        seasonal_benefits = {
            "ru": {
                "spring": {
                    "зелень": "Весенняя зелень богата витаминами после зимы",
                    "редис": "Ранний редис помогает очистить организм",
                    "лук": "Зеленый лук укрепляет иммунитет весной"
                },
                "summer": {
                    "помидоры": "Летние помидоры содержат максимум ликопина",
                    "огурцы": "Свежие огурцы помогают в жару",
                    "ягоды": "Летние ягоды - источник антиоксидантов"
                },
                "autumn": {
                    "тыква": "Осенняя тыква богата бета-каротином",
                    "яблоки": "Осенние яблоки содержат много пектина",
                    "орехи": "Орехи дают энергию перед зимой"
                },
                "winter": {
                    "цитрусы": "Зимние цитрусы - источник витамина C",
                    "капуста": "Квашеная капуста поддерживает иммунитет",
                    "корнеплоды": "Зимние корнеплоды согревают организм"
                }
            },
            "en": {
                "spring": {
                    "greens": "Spring greens are rich in vitamins after winter",
                    "radish": "Early radish helps cleanse the body",
                    "onion": "Green onions boost immunity in spring"
                },
                "summer": {
                    "tomatoes": "Summer tomatoes contain maximum lycopene",
                    "cucumbers": "Fresh cucumbers help in hot weather",
                    "berries": "Summer berries are a source of antioxidants"
                },
                "autumn": {
                    "pumpkin": "Autumn pumpkin is rich in beta-carotene",
                    "apples": "Autumn apples contain lots of pectin",
                    "nuts": "Nuts provide energy before winter"
                },
                "winter": {
                    "citrus": "Winter citrus fruits are a source of vitamin C",
                    "cabbage": "Fermented cabbage supports immunity",
                    "root_vegetables": "Winter root vegetables warm the body"
                }
            }
        }
        
        season_data = seasonal_benefits.get(language, {}).get(season, {})
        
        for key, benefit in season_data.items():
            if key in food_name.lower():
                return benefit
        
        return None
    
    def _find_product_benefits(self, food_name: str, language: str) -> Dict[str, str]:
        """Поиск пользы продукта в базе данных"""
        
        benefits = {}
        
        # Поиск по точному совпадению
        if food_name in self.benefits_database:
            product_data = self.benefits_database[food_name]
            benefits["main_benefits"] = product_data.get(language, product_data.get("en", ""))
            benefits["key_nutrients"] = product_data.get("nutrients", "")
        
        # Поиск по ключевым словам
        for product, data in self.benefits_database.items():
            if product in food_name or any(word in food_name for word in product.split()):
                benefits["main_benefits"] = data.get(language, data.get("en", ""))
                benefits["key_nutrients"] = data.get("nutrients", "")
                break
        
        return benefits
    
    def _get_personalized_benefits(self, 
                                 food_name: str, 
                                 user_goals: List[str], 
                                 language: str) -> str:
        """Получение персонализированных советов"""
        
        advice_parts = []
        
        for goal in user_goals:
            if goal == "lose_weight":
                if any(food in food_name for food in ["салат", "овощи", "зелень", "рыба"]):
                    if language == "ru":
                        advice_parts.append("Отлично подходит для похудения - низкокалорийно и питательно")
                    else:
                        advice_parts.append("Perfect for weight loss - low calorie and nutritious")
            
            elif goal == "gain_muscle":
                if any(food in food_name for food in ["мясо", "курица", "рыба", "творог", "яйца"]):
                    if language == "ru":
                        advice_parts.append("Высокое содержание белка поможет росту мышц")
                    else:
                        advice_parts.append("High protein content will help muscle growth")
            
            elif goal == "improve_energy":
                if any(food in food_name for food in ["каша", "рис", "овсянка", "фрукты"]):
                    if language == "ru":
                        advice_parts.append("Даст устойчивую энергию на долгое время")
                    else:
                        advice_parts.append("Will provide sustained energy for a long time")
        
        return " ".join(advice_parts)
    
    def _get_general_benefits(self, food_name: str, language: str) -> Dict[str, str]:
        """Получение общих принципов пользы"""
        
        benefits = {}
        
        # Определение категории продукта
        if any(word in food_name for word in ["мясо", "курица", "рыба", "говядина"]):
            if language == "ru":
                benefits["main_benefits"] = "Источник высококачественного белка, необходимого для мышц и восстановления тканей"
                benefits["key_nutrients"] = "Белок, железо, витамины группы B"
            else:
                benefits["main_benefits"] = "Source of high-quality protein essential for muscles and tissue repair"
                benefits["key_nutrients"] = "Protein, iron, B vitamins"
        
        elif any(word in food_name for word in ["овощи", "салат", "капуста", "морковь"]):
            if language == "ru":
                benefits["main_benefits"] = "Богат витаминами, минералами и клетчаткой, поддерживает пищеварение и иммунитет"
                benefits["key_nutrients"] = "Витамины A, C, K, клетчатка, антиоксиданты"
            else:
                benefits["main_benefits"] = "Rich in vitamins, minerals and fiber, supports digestion and immunity"
                benefits["key_nutrients"] = "Vitamins A, C, K, fiber, antioxidants"
        
        elif any(word in food_name for word in ["каша", "рис", "гречка", "овсянка"]):
            if language == "ru":
                benefits["main_benefits"] = "Источник сложных углеводов, дает длительную энергию и содержит важные минералы"
                benefits["key_nutrients"] = "Углеводы, клетчатка, витамины группы B, магний"
            else:
                benefits["main_benefits"] = "Source of complex carbohydrates, provides lasting energy and contains important minerals"
                benefits["key_nutrients"] = "Carbohydrates, fiber, B vitamins, magnesium"
        
        return benefits
    
    def _get_amount_context(self, nutrient_name: str, amount: float, language: str) -> str:
        """Контекст количества нутриента"""
        
        # Примерные дневные нормы (упрощенно)
        daily_norms = {
            "protein": 50,      # грамм
            "fiber": 25,        # грамм
            "calcium": 1000,    # мг
            "iron": 18,         # мг
            "vitamin_c": 90     # мг
        }
        
        norm = daily_norms.get(nutrient_name.lower(), 0)
        
        if norm > 0:
            percentage = (amount / norm) * 100
            
            if language == "ru":
                return f"({percentage:.0f}% от дневной нормы)"
            else:
                return f"({percentage:.0f}% of daily value)"
        
        return ""
    
    def _get_default_nutrient_explanation(self, nutrient_name: str, language: str) -> str:
        """Базовое объяснение для неизвестного нутриента"""
        
        if language == "ru":
            return f"{nutrient_name} важен для нормального функционирования организма"
        else:
            return f"{nutrient_name} is important for normal body function"
    
    def _load_benefits_database(self) -> Dict[str, Dict[str, str]]:
        """Загрузка базы данных пользы продуктов"""
        return {
            "курица": {
                "ru": "Отличный источник легкоусвояемого белка, поддерживает мышечную массу и иммунитет",
                "en": "Excellent source of easily digestible protein, supports muscle mass and immunity",
                "nutrients": "Белок (23г), Витамин B6, Ниацин, Селен"
            },
            "рыба": {
                "ru": "Богата омега-3 жирными кислотами, полезными для сердца и мозга",
                "en": "Rich in omega-3 fatty acids, beneficial for heart and brain health",
                "nutrients": "Белок, Омега-3, Витамин D, Йод"
            },
            "брокколи": {
                "ru": "Суперфуд с высоким содержанием витамина C и антиоксидантов",
                "en": "Superfood with high vitamin C content and antioxidants",
                "nutrients": "Витамин C, Витамин K, Фолиевая кислота, Клетчатка"
            },
            "овсянка": {
                "ru": "Источник растворимой клетчатки, помогает снизить холестерин",
                "en": "Source of soluble fiber, helps lower cholesterol",
                "nutrients": "Клетчатка, Белок, Магний, Марганец"
            },
            "яйца": {
                "ru": "Полноценный белок со всеми незаменимыми аминокислотами",
                "en": "Complete protein with all essential amino acids",
                "nutrients": "Белок, Холин, Витамин D, Селен"
            },
            "творог": {
                "ru": "Высокое содержание казеинового белка и кальция для костей",
                "en": "High in casein protein and calcium for bone health",
                "nutrients": "Белок, Кальций, Фосфор, Витамин B12"
            }
        }
    
    def _load_nutrient_functions(self) -> Dict[str, Dict[str, str]]:
        """Загрузка функций нутриентов"""
        return {
            "protein": {
                "ru": "Белок необходим для роста и восстановления мышц, синтеза ферментов и гормонов",
                "en": "Protein is essential for muscle growth and repair, enzyme and hormone synthesis"
            },
            "fiber": {
                "ru": "Клетчатка улучшает пищеварение, поддерживает здоровую микрофлору кишечника",
                "en": "Fiber improves digestion, supports healthy gut microflora"
            },
            "calcium": {
                "ru": "Кальций укрепляет кости и зубы, участвует в мышечных сокращениях",
                "en": "Calcium strengthens bones and teeth, participates in muscle contractions"
            },
            "iron": {
                "ru": "Железо необходимо для транспорта кислорода в крови",
                "en": "Iron is necessary for oxygen transport in blood"
            },
            "vitamin_c": {
                "ru": "Витамин C укрепляет иммунитет, участвует в синтезе коллагена",
                "en": "Vitamin C boosts immunity, participates in collagen synthesis"
            }
        }
    
    def _load_health_conditions_map(self) -> Dict[str, List[str]]:
        """Загрузка карты состояний здоровья"""
        return {
            "diabetes": ["низкий гликемический индекс", "контроль сахара"],
            "hypertension": ["низкое содержание натрия", "калий"],
            "anemia": ["железо", "витамин B12", "фолиевая кислота"],
            "osteoporosis": ["кальций", "витамин D", "магний"]
        }