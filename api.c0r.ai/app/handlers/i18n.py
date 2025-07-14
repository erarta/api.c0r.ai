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
                "language_current": "Current language: **{lang_name}**",
                "language_choose": "Choose your preferred language:",
                "language_changed": "✅ Language changed to **{lang_name}**",
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
                
                # Profile setup messages
                "profile_setup_age": "👶 **Step 1/6: Your Age**\n\nPlease enter your age in years (e.g., 25):",
                "profile_setup_gender": "👥 **Step 2/6: Your Gender**\n\nPlease select your gender:",
                "profile_setup_height": "📏 **Step 3/6: Your Height**\n\nPlease enter your height in centimeters (e.g., 175):",
                "profile_setup_weight": "⚖️ **Step 4/6: Your Weight**\n\nPlease enter your weight in kilograms (e.g., 70 or 70.5):",
                "profile_setup_activity": "🏃 **Step 5/6: Activity Level**\n\nPlease select your activity level:",
                "profile_setup_goal": "🎯 **Step 6/6: Your Goal**\n\nPlease select your nutrition goal:",
                "profile_setup_complete": "✅ **Profile Setup Complete!**\n\nYour daily calorie target: **{calories:,} calories**\n\nYou can now get personalized nutrition recommendations!",
                
                # Profile validation messages
                "profile_error_age": "❌ **Invalid age**\n\nPlease enter an age between 10 and 120 years:",
                "profile_error_age_number": "❌ **Invalid age format**\n\nPlease enter your age as a number (e.g., 25):",
                "profile_error_height": "❌ **Invalid height**\n\nPlease enter height between 100 and 250 cm:",
                "profile_error_height_number": "❌ **Invalid height format**\n\nPlease enter your height as a number in centimeters (e.g., 175):",
                "profile_error_weight": "❌ **Invalid weight**\n\nPlease enter weight between 30 and 300 kg:",
                "profile_error_weight_number": "❌ **Invalid weight format**\n\nPlease enter your weight as a number (e.g., 70 or 70.5):",
                
                # Profile skip messages
                "profile_skip_title": "⏭️ **Profile setup skipped**",
                "profile_skip_benefits": "💡 **Benefits of setting up a profile:**\n• Personalized daily calorie targets\n• Progress tracking\n• Better nutrition recommendations",
                "profile_skip_continue": "📸 You can still analyze food photos without a profile!",
                "profile_skip_setup_btn": "👤 Set Up Profile",
                
                # Photo analysis messages
                "photo_uploading": "Uploading and analyzing your photo... ⏳",
                "photo_no_food_title": "🤔 **No food detected in this photo**",
                "photo_no_food_tips": "📸 **Tips for better results:**\n• Make sure the food is clearly visible\n• Use good lighting\n• Focus on the food, not the background\n• Try taking the photo from above",
                "photo_no_food_try_again": "📤 **Try again with a clearer photo!**",
                "photo_no_food_credit": "💡 *Don't worry - your credit wasn't used since no food was detected.*",
                "photo_analysis_failed": "❌ **Analysis failed**\n\nThe food analysis couldn't be completed properly. Please try again with a clearer photo.\n\n💡 *Your credit wasn't used since the analysis failed.*",
                "photo_service_unavailable": "❌ **Analysis service temporarily unavailable**\n\nPlease try again in a few minutes.\n\n💡 *Your credit wasn't used since the analysis failed.*",
                "photo_error_analysis": "❌ **An error occurred during analysis**\n\nPlease try again later.\n\n💡 *Your credit wasn't used since the analysis failed.*",
                
                # Daily plan messages
                "daily_title": "📊 **Daily Plan**",
                "daily_no_profile": "🎯 To show your personalized daily nutrition plan, I need your profile information.",
                "daily_benefits": "💡 **With a profile, you'll see:**\n• Daily calorie target based on your goals\n• Real-time progress tracking\n• Nutritional balance recommendations\n• Meal planning suggestions",
                "daily_no_profile_continue": "📸 You can still analyze food photos without a profile!",
                "daily_setup_btn": "👤 Set Up Profile",
                "daily_analyze_btn": "📸 Analyze Food",
                "daily_plan_title": "📊 **Your Daily Plan** - {date}",
                "daily_goal_lose": "📉 **Goal:** Lose weight (15% calorie deficit)",
                "daily_goal_maintain": "⚖️ **Goal:** Maintain weight",
                "daily_goal_gain": "📈 **Goal:** Gain weight (15% calorie surplus)",
                "daily_goal_custom": "🎯 **Goal:** Custom plan",
                "daily_calorie_progress": "🔥 **Calorie Progress:**",
                "daily_target": "Target: {target:,} calories",
                "daily_consumed": "Consumed: {consumed:,} calories",
                "daily_remaining": "Remaining: {remaining:,} calories",
                "daily_progress": "📈 **Progress:** {progress_bar} {percent}%",
                "daily_status_on_track": "🟢 You're on track!",
                "daily_status_close": "🟡 Getting close to your target",
                "daily_status_limit": "🟠 Almost at your limit",
                "daily_status_over": "🔴 Over your daily target",
                "daily_nutrition_breakdown": "🍽️ **Nutrition Breakdown:**",
                "daily_protein": "🥩 **Protein:** {current}g / {target}g {status}",
                "daily_fats": "🥑 **Fats:** {current}g / {target}g {status}",
                "daily_carbs": "🍞 **Carbs:** {current}g / {target}g {status}",
                "daily_activity": "📱 **Today's Activity:**",
                "daily_meals_analyzed": "🍎 Meals analyzed: {count}",
                "daily_recommendations": "💡 **Recommendations:**",
                "daily_add_meal_btn": "📸 Add Meal",
                "daily_insights_btn": "🔬 Insights",
                
                # Nutrition insights messages
                "nutrition_title": "🔬 **Your Nutrition Analysis**",
                "nutrition_incomplete": "🔍 **Nutrition Insights**\n\nAlmost ready! Please complete your profile to get personalized analysis.\n\n**Missing:** {missing_fields}\n\nUse /profile to complete your information.",
                "nutrition_error": "❌ **Error**\n\nSorry, there was an error generating your nutrition insights.\n\nPlease try again or contact support if the problem persists.",
                
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
                "language_current": "Текущий язык: **{lang_name}**",
                "language_choose": "Выберите предпочитаемый язык:",
                "language_changed": "✅ Язык изменен на **{lang_name}**",
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
                
                # Profile setup messages
                "profile_setup_age": "👶 **Шаг 1/6: Ваш возраст**\n\nПожалуйста, введите ваш возраст в годах (например, 25):",
                "profile_setup_gender": "👥 **Шаг 2/6: Ваш пол**\n\nПожалуйста, выберите ваш пол:",
                "profile_setup_height": "📏 **Шаг 3/6: Ваш рост**\n\nПожалуйста, введите ваш рост в сантиметрах (например, 175):",
                "profile_setup_weight": "⚖️ **Шаг 4/6: Ваш вес**\n\nПожалуйста, введите ваш вес в килограммах (например, 70 или 70.5):",
                "profile_setup_activity": "🏃 **Шаг 5/6: Уровень активности**\n\nПожалуйста, выберите ваш уровень активности:",
                "profile_setup_goal": "🎯 **Шаг 6/6: Ваша цель**\n\nПожалуйста, выберите вашу цель по питанию:",
                "profile_setup_complete": "✅ **Настройка профиля завершена!**\n\nВаша дневная цель калорий: **{calories:,} калорий**\n\nТеперь вы можете получать персональные рекомендации по питанию!",
                
                # Profile validation messages
                "profile_error_age": "❌ **Неверный возраст**\n\nПожалуйста, введите возраст от 10 до 120 лет:",
                "profile_error_age_number": "❌ **Неверный формат возраста**\n\nПожалуйста, введите ваш возраст числом (например, 25):",
                "profile_error_height": "❌ **Неверный рост**\n\nПожалуйста, введите рост от 100 до 250 см:",
                "profile_error_height_number": "❌ **Неверный формат роста**\n\nПожалуйста, введите ваш рост числом в сантиметрах (например, 175):",
                "profile_error_weight": "❌ **Неверный вес**\n\nПожалуйста, введите вес от 30 до 300 кг:",
                "profile_error_weight_number": "❌ **Неверный формат веса**\n\nПожалуйста, введите ваш вес числом (например, 70 или 70.5):",
                
                # Profile skip messages
                "profile_skip_title": "⏭️ **Настройка профиля пропущена**",
                "profile_skip_benefits": "💡 **Преимущества настройки профиля:**\n• Персональные дневные цели калорий\n• Отслеживание прогресса\n• Лучшие рекомендации по питанию",
                "profile_skip_continue": "📸 Вы все еще можете анализировать фото еды без профиля!",
                "profile_skip_setup_btn": "👤 Настроить профиль",
                
                # Photo analysis messages
                "photo_uploading": "Загружаю и анализирую ваше фото... ⏳",
                "photo_no_food_title": "🤔 **В этом фото не обнаружена еда**",
                "photo_no_food_tips": "📸 **Советы для лучших результатов:**\n• Убедитесь, что еда хорошо видна\n• Используйте хорошее освещение\n• Фокусируйтесь на еде, а не на фоне\n• Попробуйте сфотографировать сверху",
                "photo_no_food_try_again": "📤 **Попробуйте снова с более четким фото!**",
                "photo_no_food_credit": "💡 *Не беспокойтесь - ваш кредит не был использован, так как еда не была обнаружена.*",
                "photo_analysis_failed": "❌ **Анализ не удался**\n\nАнализ еды не мог быть выполнен должным образом. Пожалуйста, попробуйте снова с более четким фото.\n\n💡 *Ваш кредит не был использован, так как анализ не удался.*",
                "photo_service_unavailable": "❌ **Служба анализа временно недоступна**\n\nПожалуйста, попробуйте через несколько минут.\n\n💡 *Ваш кредит не был использован, так как анализ не удался.*",
                "photo_error_analysis": "❌ **Произошла ошибка во время анализа**\n\nПожалуйста, попробуйте позже.\n\n💡 *Ваш кредит не был использован, так как анализ не удался.*",
                
                # Daily plan messages
                "daily_title": "📊 **Дневной план**",
                "daily_no_profile": "🎯 Чтобы показать ваш персональный дневной план питания, мне нужна информация о вашем профиле.",
                "daily_benefits": "💡 **С профилем вы увидите:**\n• Дневную цель калорий на основе ваших целей\n• Отслеживание прогресса в реальном времени\n• Рекомендации по балансу питания\n• Предложения по планированию приемов пищи",
                "daily_no_profile_continue": "📸 Вы все еще можете анализировать фото еды без профиля!",
                "daily_setup_btn": "👤 Настроить профиль",
                "daily_analyze_btn": "📸 Анализировать еду",
                "daily_plan_title": "📊 **Ваш дневной план** - {date}",
                "daily_goal_lose": "📉 **Цель:** Похудение (дефицит 15% калорий)",
                "daily_goal_maintain": "⚖️ **Цель:** Поддержание веса",
                "daily_goal_gain": "📈 **Цель:** Набор веса (избыток 15% калорий)",
                "daily_goal_custom": "🎯 **Цель:** Персональный план",
                "daily_calorie_progress": "🔥 **Прогресс калорий:**",
                "daily_target": "Цель: {target:,} калорий",
                "daily_consumed": "Потреблено: {consumed:,} калорий",
                "daily_remaining": "Осталось: {remaining:,} калорий",
                "daily_progress": "📈 **Прогресс:** {progress_bar} {percent}%",
                "daily_status_on_track": "🟢 Вы на правильном пути!",
                "daily_status_close": "🟡 Приближаетесь к цели",
                "daily_status_limit": "🟠 Почти достигли лимита",
                "daily_status_over": "🔴 Превысили дневную цель",
                "daily_nutrition_breakdown": "🍽️ **Разбор питания:**",
                "daily_protein": "🥩 **Белки:** {current}г / {target}г {status}",
                "daily_fats": "🥑 **Жиры:** {current}г / {target}г {status}",
                "daily_carbs": "🍞 **Углеводы:** {current}г / {target}г {status}",
                "daily_activity": "📱 **Активность сегодня:**",
                "daily_meals_analyzed": "🍎 Проанализировано приемов пищи: {count}",
                "daily_recommendations": "💡 **Рекомендации:**",
                "daily_add_meal_btn": "📸 Добавить прием пищи",
                "daily_insights_btn": "🔬 Анализ",
                
                # Nutrition insights messages
                "nutrition_title": "🔬 **Ваш анализ питания**",
                "nutrition_incomplete": "🔍 **Анализ питания**\n\nПочти готово! Пожалуйста, завершите настройку профиля для получения персонального анализа.\n\n**Отсутствует:** {missing_fields}\n\nИспользуйте /profile для завершения информации.",
                "nutrition_error": "❌ **Ошибка**\n\nИзвините, произошла ошибка при создании анализа питания.\n\nПожалуйста, попробуйте снова или обратитесь в поддержку, если проблема сохраняется.",
                
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