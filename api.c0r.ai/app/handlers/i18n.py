"""
Internationalization (i18n) module for c0r.ai Telegram Bot
Handles language detection, translations, and language switching
"""
from typing import Dict, Optional, List
from enum import Enum
import re
from loguru import logger


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    RUSSIAN = "ru"


class I18nManager:
    """Manages internationalization for the bot"""
    
    # Countries that default to Russian
    RUSSIAN_COUNTRIES = {
        "RU",  # Russia
        "BY",  # Belarus
        "KZ",  # Kazakhstan
        "KG",  # Kyrgyzstan
        "AM",  # Armenia
        "AZ",  # Azerbaijan
        "GE",  # Georgia
        "UZ",  # Uzbekistan
    }
    
    # Phone number patterns for Russian-speaking countries
    RUSSIAN_PHONE_PATTERNS = [
        r'^\+7',  # +7 (Russia)
        r'^8',    # 8 (Russia)
        r'^\+375',  # +375 (Belarus)
        r'^\+7[0-9]{10}$',  # +7XXXXXXXXXX
        r'^8[0-9]{10}$',    # 8XXXXXXXXXX
    ]
    
    def __init__(self):
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load all translations"""
        return {
            Language.ENGLISH.value: {
                # Welcome messages
                "welcome_title": "🎉 **Welcome to c0r.ai Food Analyzer!**",
                "welcome_greeting": "👋 Hello {name}!",
                "welcome_credits": "💳 You have **{credits} credits** remaining",
                "welcome_features": "🍎 **What I can do:**",
                "welcome_feature_1": "• Analyze your food photos for calories, protein, fats, carbs",
                "welcome_feature_2": "• Calculate your daily calorie needs",
                "welcome_feature_3": "• Track your nutrition goals",
                "welcome_ready": "🚀 **Ready to start?** Choose an option below:",
                
                # Menu buttons
                "btn_analyze_food": "🍕 Analyze Food Photo",
                "btn_check_status": "📊 Check My Status",
                "btn_help_guide": "ℹ️ Help & Guide",
                "btn_buy_credits": "💳 Buy More Credits",
                "btn_my_profile": "👤 My Profile",
                "btn_main_menu": "🏠 Main Menu",
                "btn_nutrition_insights": "🔬 Nutrition Insights",
                "btn_daily_plan": "📅 Daily Plan",
                "btn_weekly_report": "📈 Weekly Report",
                "btn_water_tracker": "💧 Water Tracker",
                "btn_language": "🌐 Language",
                
                # Help messages
                "help_title": "🤖 **c0r.ai Food Analyzer - Help Guide**",
                "help_usage_title": "📸 **How to use:**",
                "help_usage_1": "1. Send me a food photo",
                "help_usage_2": "2. I'll analyze calories, protein, fats, and carbs",
                "help_usage_3": "3. Get instant nutrition information",
                "help_credits_title": "🆓 **Free credits:**",
                "help_credits_1": "• You start with 3 free credits",
                "help_credits_2": "• Each photo analysis costs 1 credit",
                "help_features_title": "🎯 **Features:**",
                "help_features_1": "• Accurate calorie counting",
                "help_features_2": "• Detailed macro breakdown",
                "help_features_3": "• Daily calorie calculation",
                "help_features_4": "• Personal nutrition tracking",
                "help_commands_title": "💡 **Commands:**",
                "help_commands_1": "• /start - Main menu with interactive buttons",
                "help_commands_2": "• /help - This help guide",
                "help_commands_3": "• /status - Check your account status",
                "help_commands_4": "• /buy - Purchase more credits",
                "help_commands_5": "• /profile - Set up your personal profile",
                "help_commands_6": "• /daily - View daily nutrition plan & progress",
                "help_credits_need": "💳 **Need more credits?**",
                "help_credits_info": "Use /buy to purchase additional credits when you run out.",
                "help_support": "📞 **Support:** Contact team@c0r.ai",
                
                # Status messages
                "status_title": "📊 *Your Account Status*",
                "status_user_id": "🆔 User ID: `{user_id}`",
                "status_credits": "💳 Credits remaining: *{credits}*",
                "status_total_paid": "💰 Total paid: *{total_paid:.2f} RUB*",
                "status_member_since": "📅 Member since: `{date}`",
                "status_system": "🤖 System: *c0r.ai v{version}*",
                "status_online": "🌐 Status: *Online*",
                "status_powered_by": "⚡ Powered by c0r AI Vision",
                
                # Payment messages
                "payment_title": "💳 **Purchase Credits**",
                "payment_description": "Choose a plan to get more credits for food analysis:",
                "payment_basic_title": "Basic Plan",
                "payment_basic_desc": "20 credits for food analysis",
                "payment_pro_title": "Pro Plan",
                "payment_pro_desc": "100 credits for food analysis",
                "payment_price": "{price} RUB",
                "payment_credits": "{credits} credits",
                
                # Error messages
                "error_general": "An error occurred. Please try again later.",
                "error_status": "An error occurred while fetching your status. Please try again later.",
                "error_rate_limit_title": "⏳ **Too many requests!**",
                "error_rate_limit_general": "🚫 Maximum 20 commands per minute\n⏰ Try again in {remaining} seconds",
                "error_rate_limit_photo_title": "⏳ **Photo analysis rate limit reached!**",
                "error_rate_limit_photo": "🚫 You can analyze maximum 5 photos per minute\n⏰ Try again in {remaining} seconds\n\n💡 This prevents system overload and ensures fair usage for all users.",
                "error_file_type": "❌ **File type not supported: {file_type}**\n\n🖼️ **Please send only photos** for food analysis.\n💡 Make sure to use the 📷 **Photo** option in Telegram, not 📎 **File/Document**.",
                
                # Language messages
                "language_title": "🌐 **Language Settings**",
                "language_current": "Current language: **{language}**",
                "language_choose": "Choose your preferred language:",
                "language_changed": "✅ Language changed to **{language}**",
                "language_english": "🇺🇸 English",
                "language_russian": "🇷🇺 Русский",
                
                # Profile messages
                "profile_title": "👤 **My Profile**",
                "profile_setup_needed": "📝 **Profile Setup Required**\n\nTo get personalized nutrition recommendations, please set up your profile.",
                "profile_setup_btn": "⚙️ Set Up Profile",
                "profile_info_title": "👤 **Profile Information**",
                "profile_age": "Age: {age} years",
                "profile_gender": "Gender: {gender}",
                "profile_height": "Height: {height} cm",
                "profile_weight": "Weight: {weight} kg",
                "profile_activity": "Activity: {activity}",
                "profile_goal": "Goal: {goal}",
                "profile_calories": "Daily calories target: {calories}",
                "profile_edit_btn": "✏️ Edit Profile",
                
                # Main menu
                "main_menu_title": "🚀 **Choose an option:**",
            },
            
            Language.RUSSIAN.value: {
                # Welcome messages
                "welcome_title": "🎉 **Добро пожаловать в c0r.ai Анализатор еды!**",
                "welcome_greeting": "👋 Привет, {name}!",
                "welcome_credits": "💳 У вас осталось **{credits} кредитов**",
                "welcome_features": "🍎 **Что я умею:**",
                "welcome_feature_1": "• Анализирую фотографии еды на калории, белки, жиры, углеводы",
                "welcome_feature_2": "• Рассчитываю ваши дневные потребности в калориях",
                "welcome_feature_3": "• Отслеживаю ваши цели по питанию",
                "welcome_ready": "🚀 **Готовы начать?** Выберите опцию ниже:",
                
                # Menu buttons
                "btn_analyze_food": "🍕 Анализировать фото еды",
                "btn_check_status": "📊 Проверить статус",
                "btn_help_guide": "ℹ️ Помощь и руководство",
                "btn_buy_credits": "💳 Купить кредиты",
                "btn_my_profile": "👤 Мой профиль",
                "btn_main_menu": "🏠 Главное меню",
                "btn_nutrition_insights": "🔬 Анализ питания",
                "btn_daily_plan": "📅 Дневной план",
                "btn_weekly_report": "📈 Недельный отчет",
                "btn_water_tracker": "💧 Трекер воды",
                "btn_language": "🌐 Язык",
                
                # Help messages
                "help_title": "🤖 **c0r.ai Анализатор еды - Руководство**",
                "help_usage_title": "📸 **Как использовать:**",
                "help_usage_1": "1. Отправьте мне фото еды",
                "help_usage_2": "2. Я проанализирую калории, белки, жиры и углеводы",
                "help_usage_3": "3. Получите мгновенную информацию о питании",
                "help_credits_title": "🆓 **Бесплатные кредиты:**",
                "help_credits_1": "• Вы начинаете с 3 бесплатных кредитов",
                "help_credits_2": "• Каждый анализ фото стоит 1 кредит",
                "help_features_title": "🎯 **Возможности:**",
                "help_features_1": "• Точный подсчет калорий",
                "help_features_2": "• Детальный анализ макронутриентов",
                "help_features_3": "• Расчет дневных калорий",
                "help_features_4": "• Персональное отслеживание питания",
                "help_commands_title": "💡 **Команды:**",
                "help_commands_1": "• /start - Главное меню с интерактивными кнопками",
                "help_commands_2": "• /help - Это руководство",
                "help_commands_3": "• /status - Проверить статус аккаунта",
                "help_commands_4": "• /buy - Купить больше кредитов",
                "help_commands_5": "• /profile - Настроить личный профиль",
                "help_commands_6": "• /daily - Просмотр дневного плана питания и прогресса",
                "help_credits_need": "💳 **Нужно больше кредитов?**",
                "help_credits_info": "Используйте /buy для покупки дополнительных кредитов.",
                "help_support": "📞 **Поддержка:** Обратитесь к team@c0r.ai",
                
                # Status messages
                "status_title": "📊 *Статус вашего аккаунта*",
                "status_user_id": "🆔 ID пользователя: `{user_id}`",
                "status_credits": "💳 Осталось кредитов: *{credits}*",
                "status_total_paid": "💰 Всего оплачено: *{total_paid:.2f} RUB*",
                "status_member_since": "📅 Участник с: `{date}`",
                "status_system": "🤖 Система: *c0r.ai v{version}*",
                "status_online": "🌐 Статус: *Онлайн*",
                "status_powered_by": "⚡ Работает на c0r AI Vision",
                
                # Payment messages
                "payment_title": "💳 **Покупка кредитов**",
                "payment_description": "Выберите план для получения большего количества кредитов для анализа еды:",
                "payment_basic_title": "Базовый план",
                "payment_basic_desc": "20 кредитов для анализа еды",
                "payment_pro_title": "Про план",
                "payment_pro_desc": "100 кредитов для анализа еды",
                "payment_price": "{price} RUB",
                "payment_credits": "{credits} кредитов",
                
                # Error messages
                "error_general": "Произошла ошибка. Пожалуйста, попробуйте позже.",
                "error_status": "Произошла ошибка при получении вашего статуса. Пожалуйста, попробуйте позже.",
                "error_rate_limit_title": "⏳ **Слишком много запросов!**",
                "error_rate_limit_general": "🚫 Максимум 20 команд в минуту\n⏰ Попробуйте через {remaining} секунд",
                "error_rate_limit_photo_title": "⏳ **Достигнут лимит анализа фото!**",
                "error_rate_limit_photo": "🚫 Вы можете анализировать максимум 5 фото в минуту\n⏰ Попробуйте через {remaining} секунд\n\n💡 Это предотвращает перегрузку системы и обеспечивает справедливое использование для всех пользователей.",
                "error_file_type": "❌ **Неподдерживаемый тип файла: {file_type}**\n\n🖼️ **Пожалуйста, отправляйте только фотографии** для анализа еды.\n💡 Убедитесь, что используете опцию 📷 **Фото** в Telegram, а не 📎 **Файл/Документ**.",
                
                # Language messages
                "language_title": "🌐 **Настройки языка**",
                "language_current": "Текущий язык: **{language}**",
                "language_choose": "Выберите предпочитаемый язык:",
                "language_changed": "✅ Язык изменен на **{language}**",
                "language_english": "🇺🇸 English",
                "language_russian": "🇷🇺 Русский",
                
                # Profile messages
                "profile_title": "👤 **Мой профиль**",
                "profile_setup_needed": "📝 **Требуется настройка профиля**\n\nДля получения персональных рекомендаций по питанию, пожалуйста, настройте ваш профиль.",
                "profile_setup_btn": "⚙️ Настроить профиль",
                "profile_info_title": "👤 **Информация профиля**",
                "profile_age": "Возраст: {age} лет",
                "profile_gender": "Пол: {gender}",
                "profile_height": "Рост: {height} см",
                "profile_weight": "Вес: {weight} кг",
                "profile_activity": "Активность: {activity}",
                "profile_goal": "Цель: {goal}",
                "profile_calories": "Дневная цель калорий: {calories}",
                "profile_edit_btn": "✏️ Редактировать профиль",
                
                # Main menu
                "main_menu_title": "🚀 **Выберите опцию:**",
            }
        }
    
    def detect_language(self, user_country: Optional[str] = None, phone_number: Optional[str] = None) -> str:
        """
        Detect user's preferred language based on country and phone number
        
        Args:
            user_country: User's country code (e.g., 'RU', 'US')
            phone_number: User's phone number
            
        Returns:
            Language code ('en' or 'ru')
        """
        # Check country first
        if user_country and user_country.upper() in self.RUSSIAN_COUNTRIES:
            logger.info(f"Detected Russian language for country: {user_country}")
            return Language.RUSSIAN.value
        
        # Check phone number patterns
        if phone_number:
            for pattern in self.RUSSIAN_PHONE_PATTERNS:
                if re.match(pattern, phone_number):
                    logger.info(f"Detected Russian language for phone: {phone_number}")
                    return Language.RUSSIAN.value
        
        # Default to English
        logger.info(f"Defaulting to English language for country: {user_country}, phone: {phone_number}")
        return Language.ENGLISH.value
    
    def get_text(self, key: str, language: str = Language.ENGLISH.value, **kwargs) -> str:
        """
        Get translated text for a given key and language
        
        Args:
            key: Translation key
            language: Language code ('en' or 'ru')
            **kwargs: Format parameters for the text
            
        Returns:
            Translated and formatted text
        """
        if language not in self.translations:
            logger.warning(f"Language {language} not found, falling back to English")
            language = Language.ENGLISH.value
        
        if key not in self.translations[language]:
            logger.warning(f"Translation key '{key}' not found for language {language}")
            # Fallback to English
            if key in self.translations[Language.ENGLISH.value]:
                text = self.translations[Language.ENGLISH.value][key]
            else:
                return f"[Missing translation: {key}]"
        else:
            text = self.translations[language][key]
        
        # Format the text with provided parameters
        try:
            return text.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing format parameter {e} for key '{key}' in language {language}")
            return text
    
    def get_language_name(self, language_code: str) -> str:
        """Get human-readable language name"""
        language_names = {
            Language.ENGLISH.value: "English",
            Language.RUSSIAN.value: "Русский"
        }
        return language_names.get(language_code, "Unknown")


# Global instance
i18n = I18nManager() 