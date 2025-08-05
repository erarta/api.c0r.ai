"""
Motivation and Praise System for c0r.AI ML Service
Provides personalized motivation messages and encouragement
"""

from typing import Dict, List, Optional
from datetime import datetime
import random
from loguru import logger


class MotivationSystem:
    """Система мотивации и поощрения пользователей"""
    
    def __init__(self):
        self.motivation_messages = self._load_motivation_messages()
        self.encouragement_messages = self._load_encouragement_messages()
        self.cooking_motivations = self._load_cooking_motivations()
        
        logger.info("🎉 MotivationSystem initialized")
    
    def get_motivation_greeting(self, 
                              language: str, 
                              level: str = "standard",
                              analysis_count: int = 0) -> str:
        """
        Получение мотивационного приветствия
        
        Args:
            language: Язык пользователя
            level: Уровень мотивации (standard, high, celebration)
            analysis_count: Количество проведенных анализов
            
        Returns:
            Персонализированное мотивационное сообщение
        """
        logger.debug(f"🎯 Generating motivation greeting: {language}, level={level}, count={analysis_count}")
        
        # Определяем категорию на основе количества анализов
        if analysis_count == 0:
            category = "first_time"
        elif analysis_count < 10:
            category = "beginner"
        elif analysis_count < 50:
            category = "regular"
        elif analysis_count < 100:
            category = "experienced"
        else:
            category = "expert"
        
        messages = self.motivation_messages.get(language, {}).get(category, [])
        
        if not messages:
            # Fallback на английский если нет перевода
            messages = self.motivation_messages.get("en", {}).get(category, [])
        
        if messages:
            base_message = random.choice(messages)
            
            # Добавляем специальные элементы в зависимости от уровня
            if level == "high":
                return self._enhance_motivation_message(base_message, language, "high")
            elif level == "celebration":
                return self._enhance_motivation_message(base_message, language, "celebration")
            else:
                return base_message
        
        # Базовое сообщение если ничего не найдено
        return "🍽️ Отлично! Давайте проанализируем ваше блюдо!" if language == "ru" else "🍽️ Great! Let's analyze your dish!"
    
    def get_encouragement_message(self, 
                                language: str, 
                                context: str = "healthy_choice") -> str:
        """
        Получение поощрительного сообщения
        
        Args:
            language: Язык пользователя
            context: Контекст поощрения (healthy_choice, progress, achievement)
            
        Returns:
            Поощрительное сообщение
        """
        logger.debug(f"💪 Generating encouragement: {language}, context={context}")
        
        messages = self.encouragement_messages.get(language, {}).get(context, [])
        
        if not messages:
            # Fallback на английский
            messages = self.encouragement_messages.get("en", {}).get(context, [])
        
        return random.choice(messages) if messages else "Отличная работа!" if language == "ru" else "Great job!"
    
    def get_cooking_motivation(self, 
                             language: str, 
                             cooking_level: str = "beginner") -> str:
        """
        Получение мотивации для готовки
        
        Args:
            language: Язык пользователя
            cooking_level: Уровень готовки (beginner, intermediate, advanced)
            
        Returns:
            Мотивационное сообщение для готовки
        """
        logger.debug(f"👨‍🍳 Generating cooking motivation: {language}, level={cooking_level}")
        
        messages = self.cooking_motivations.get(language, {}).get(cooking_level, [])
        
        if not messages:
            # Fallback на английский
            messages = self.cooking_motivations.get("en", {}).get(cooking_level, [])
        
        return random.choice(messages) if messages else "Готовим вместе!" if language == "ru" else "Let's cook together!"
    
    def get_milestone_celebration(self, 
                                language: str, 
                                milestone_type: str,
                                value: int) -> str:
        """
        Получение празднования достижения
        
        Args:
            language: Язык пользователя
            milestone_type: Тип достижения (analyses, recipes, days_streak)
            value: Значение достижения
            
        Returns:
            Празднование достижения
        """
        logger.info(f"🎊 Milestone celebration: {milestone_type}={value}")
        
        if language == "ru":
            celebrations = {
                "analyses": {
                    10: "🎉 Поздравляем! Вы провели уже 10 анализов блюд! Вы на правильном пути к здоровому питанию!",
                    50: "🌟 Невероятно! 50 анализов! Вы настоящий эксперт по здоровому питанию!",
                    100: "🏆 Фантастика! 100 анализов блюд! Вы достигли уровня мастера здорового питания!",
                    500: "👑 Легенда! 500 анализов! Вы - настоящий гуру здорового образа жизни!"
                },
                "recipes": {
                    5: "👨‍🍳 Отлично! Вы уже создали 5 рецептов! Продолжайте готовить здоровую еду!",
                    25: "🍳 Браво! 25 рецептов! Вы становитесь настоящим шеф-поваром!",
                    100: "🥇 Потрясающе! 100 рецептов! Вы - мастер кулинарного искусства!"
                },
                "days_streak": {
                    7: "📅 Неделя здорового питания! Отличное начало!",
                    30: "🗓️ Месяц осознанного питания! Вы формируете отличные привычки!",
                    100: "⭐ 100 дней здорового образа жизни! Вы - пример для подражания!"
                }
            }
        else:
            celebrations = {
                "analyses": {
                    10: "🎉 Congratulations! You've completed 10 food analyses! You're on the right track to healthy eating!",
                    50: "🌟 Amazing! 50 analyses! You're becoming a real healthy eating expert!",
                    100: "🏆 Fantastic! 100 food analyses! You've reached master level in healthy nutrition!",
                    500: "👑 Legend! 500 analyses! You're a true healthy lifestyle guru!"
                },
                "recipes": {
                    5: "👨‍🍳 Excellent! You've created 5 recipes! Keep cooking healthy food!",
                    25: "🍳 Bravo! 25 recipes! You're becoming a real chef!",
                    100: "🥇 Amazing! 100 recipes! You're a master of culinary art!"
                },
                "days_streak": {
                    7: "📅 A week of healthy eating! Great start!",
                    30: "🗓️ A month of mindful nutrition! You're building excellent habits!",
                    100: "⭐ 100 days of healthy lifestyle! You're an inspiration!"
                }
            }
        
        milestone_celebrations = celebrations.get(milestone_type, {})
        
        # Находим ближайшее достижение
        for threshold in sorted(milestone_celebrations.keys(), reverse=True):
            if value >= threshold:
                return milestone_celebrations[threshold]
        
        # Базовое поздравление
        return f"🎊 Поздравляем с достижением!" if language == "ru" else f"🎊 Congratulations on your achievement!"
    
    def _enhance_motivation_message(self, 
                                  base_message: str, 
                                  language: str, 
                                  enhancement_type: str) -> str:
        """Улучшение мотивационного сообщения"""
        
        if enhancement_type == "high":
            if language == "ru":
                enhancers = ["💪 ", "🔥 ", "⚡ ", "🌟 "]
                suffix = " Вы делаете отличную работу!"
            else:
                enhancers = ["💪 ", "🔥 ", "⚡ ", "🌟 "]
                suffix = " You're doing amazing work!"
        elif enhancement_type == "celebration":
            if language == "ru":
                enhancers = ["🎉 ", "🎊 ", "🥳 ", "🏆 "]
                suffix = " Это достижение заслуживает празднования!"
            else:
                enhancers = ["🎉 ", "🎊 ", "🥳 ", "🏆 "]
                suffix = " This achievement deserves celebration!"
        else:
            return base_message
        
        enhancer = random.choice(enhancers)
        return f"{enhancer}{base_message}{suffix}"
    
    def _load_motivation_messages(self) -> Dict[str, Dict[str, List[str]]]:
        """Загрузка мотивационных сообщений"""
        return {
            "ru": {
                "first_time": [
                    "🌟 Добро пожаловать в мир осознанного питания! Давайте начнем ваш путь к здоровью!",
                    "🎯 Отличное решение начать отслеживать питание! Каждый шаг важен!",
                    "💚 Здорово, что вы заботитесь о своем здоровье! Начинаем анализ!",
                    "🚀 Первый шаг к здоровому образу жизни! Вы на правильном пути!"
                ],
                "beginner": [
                    "👍 Вы уже делаете успехи в отслеживании питания! Продолжаем!",
                    "📈 Каждый анализ приближает вас к цели! Отличная работа!",
                    "🎪 Вы формируете полезные привычки! Так держать!",
                    "💪 Ваша настойчивость впечатляет! Анализируем дальше!"
                ],
                "regular": [
                    "🏃‍♂️ Вы уже опытный пользователь! Ваши знания о питании растут!",
                    "📊 Отличная последовательность в отслеживании! Вы молодец!",
                    "🎯 Вы становитесь экспертом в здоровом питании! Продолжаем!",
                    "⭐ Ваша дисциплина в питании заслуживает уважения!"
                ],
                "experienced": [
                    "🧠 Вы настоящий знаток здорового питания! Впечатляюще!",
                    "🏆 Ваш опыт в анализе питания впечатляет! Вы эксперт!",
                    "👨‍🎓 Вы могли бы учить других здоровому питанию!",
                    "🌟 Ваши знания о питании на высочайшем уровне!"
                ],
                "expert": [
                    "👑 Вы - мастер здорового питания! Невероятные результаты!",
                    "🥇 Ваша экспертиза в питании поражает! Вы легенда!",
                    "🎖️ Такой уровень знаний о питании встречается редко!",
                    "🌟 Вы - настоящий гуру здорового образа жизни!"
                ]
            },
            "en": {
                "first_time": [
                    "🌟 Welcome to the world of mindful nutrition! Let's start your health journey!",
                    "🎯 Great decision to start tracking your nutrition! Every step matters!",
                    "💚 It's wonderful that you care about your health! Let's begin the analysis!",
                    "🚀 First step towards a healthy lifestyle! You're on the right path!"
                ],
                "beginner": [
                    "👍 You're already making progress in nutrition tracking! Let's continue!",
                    "📈 Each analysis brings you closer to your goal! Excellent work!",
                    "🎪 You're building healthy habits! Keep it up!",
                    "💪 Your persistence is impressive! Let's analyze further!"
                ],
                "regular": [
                    "🏃‍♂️ You're already an experienced user! Your nutrition knowledge is growing!",
                    "📊 Excellent consistency in tracking! You're doing great!",
                    "🎯 You're becoming a healthy eating expert! Let's continue!",
                    "⭐ Your discipline in nutrition deserves respect!"
                ],
                "experienced": [
                    "🧠 You're a true healthy eating connoisseur! Impressive!",
                    "🏆 Your experience in nutrition analysis is impressive! You're an expert!",
                    "👨‍🎓 You could teach others about healthy eating!",
                    "🌟 Your nutrition knowledge is at the highest level!"
                ],
                "expert": [
                    "👑 You're a master of healthy eating! Incredible results!",
                    "🥇 Your nutrition expertise is astounding! You're a legend!",
                    "🎖️ Such level of nutrition knowledge is rare!",
                    "🌟 You're a true healthy lifestyle guru!"
                ]
            }
        }
    
    def _load_encouragement_messages(self) -> Dict[str, Dict[str, List[str]]]:
        """Загрузка поощрительных сообщений"""
        return {
            "ru": {
                "healthy_choice": [
                    "💚 Отличный выбор здоровой еды! Ваше тело скажет вам спасибо!",
                    "🌱 Такое питание дает энергию и силы! Продолжайте в том же духе!",
                    "✨ Вы заботитесь о своем здоровье - это вдохновляет!",
                    "🎯 Каждое здоровое блюдо - шаг к лучшей версии себя!",
                    "🌟 Ваш выбор в пользу здоровья делает вас сильнее!"
                ],
                "progress": [
                    "📈 Ваш прогресс в здоровом питании заметен! Так держать!",
                    "🚀 Вы движетесь к своей цели уверенными шагами!",
                    "💪 Каждый день вы становитесь здоровее! Отлично!",
                    "⭐ Ваши усилия приносят результаты! Продолжайте!"
                ],
                "achievement": [
                    "🏆 Поздравляем с достижением! Вы большой молодец!",
                    "🎉 Это заслуженная победа! Ваши усилия окупились!",
                    "👏 Браво! Такие результаты впечатляют!",
                    "🌟 Вы достигли новой высоты! Гордитесь собой!"
                ]
            },
            "en": {
                "healthy_choice": [
                    "💚 Excellent healthy food choice! Your body will thank you!",
                    "🌱 Such nutrition gives energy and strength! Keep it up!",
                    "✨ You care about your health - that's inspiring!",
                    "🎯 Every healthy dish is a step towards a better version of yourself!",
                    "🌟 Your choice for health makes you stronger!"
                ],
                "progress": [
                    "📈 Your progress in healthy eating is noticeable! Keep it up!",
                    "🚀 You're moving towards your goal with confident steps!",
                    "💪 Every day you become healthier! Excellent!",
                    "⭐ Your efforts are paying off! Continue!"
                ],
                "achievement": [
                    "🏆 Congratulations on your achievement! You're doing great!",
                    "🎉 This is a well-deserved victory! Your efforts paid off!",
                    "👏 Bravo! Such results are impressive!",
                    "🌟 You've reached a new height! Be proud of yourself!"
                ]
            }
        }
    
    def _load_cooking_motivations(self) -> Dict[str, Dict[str, List[str]]]:
        """Загрузка мотиваций для готовки"""
        return {
            "ru": {
                "beginner": [
                    "👨‍🍳 Готовка - это искусство, которому можно научиться! Начинаем с простого!",
                    "🍳 Каждый великий повар когда-то был новичком! Вы на правильном пути!",
                    "📚 Изучение новых рецептов расширяет кулинарные горизонты!",
                    "💡 Простые рецепты могут быть невероятно вкусными! Попробуем!"
                ],
                "intermediate": [
                    "🎯 Ваши навыки готовки растут! Время для новых вызовов!",
                    "🌟 Вы уже умеете готовить базовые блюда! Усложняем задачу!",
                    "🚀 Готовы к более интересным рецептам? Вперед!",
                    "💪 Ваш опыт позволяет экспериментировать! Творим!"
                ],
                "advanced": [
                    "👑 Вы настоящий мастер кухни! Создаем кулинарные шедевры!",
                    "🏆 Ваши навыки готовки впечатляют! Время для авторских рецептов!",
                    "🎨 Готовка для вас - это искусство! Творите без границ!",
                    "⭐ Вы можете справиться с любым рецептом! Вызов принят!"
                ]
            },
            "en": {
                "beginner": [
                    "👨‍🍳 Cooking is an art that can be learned! Let's start simple!",
                    "🍳 Every great chef was once a beginner! You're on the right path!",
                    "📚 Learning new recipes expands culinary horizons!",
                    "💡 Simple recipes can be incredibly delicious! Let's try!"
                ],
                "intermediate": [
                    "🎯 Your cooking skills are growing! Time for new challenges!",
                    "🌟 You can already cook basic dishes! Let's make it more complex!",
                    "🚀 Ready for more interesting recipes? Let's go!",
                    "💪 Your experience allows experimentation! Let's create!"
                ],
                "advanced": [
                    "👑 You're a true kitchen master! Creating culinary masterpieces!",
                    "🏆 Your cooking skills are impressive! Time for signature recipes!",
                    "🎨 Cooking is art for you! Create without boundaries!",
                    "⭐ You can handle any recipe! Challenge accepted!"
                ]
            }
        }