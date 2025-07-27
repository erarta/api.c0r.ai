# Обновления интернационализации для AIDI.APP

*Дата создания: 27 января 2025*
*Цель: Адаптация переводов от питания к кибербезопасности и репутации*

## 📋 Обзор изменений i18n

### Текущая структура i18n (c0r.ai)
```
i18n/
├── en/                        # Английские переводы
│   ├── welcome.py            # Приветственные сообщения
│   ├── help.py              # Справочная информация
│   ├── profile.py           # Управление профилем
│   ├── payments.py          # Платежные сообщения
│   ├── errors.py            # Сообщения об ошибках
│   ├── nutrition.py         # ❌ Анализ питания (удаляем)
│   ├── daily.py             # ❌ Ежедневная статистика (удаляем)
│   ├── recipes.py           # ❌ Генерация рецептов (удаляем)
│   └── reports.py           # ✅ Отчеты (адаптируем)
└── ru/                       # Русские переводы (зеркальная структура)
```

### Новая структура i18n (AIDI.APP)
```
i18n/
├── en/                        # Английские переводы
│   ├── welcome.py            # ✅ Приветственные сообщения (адаптируем)
│   ├── help.py              # ✅ Справочная информация (адаптируем)
│   ├── profile.py           # ✅ Управление профилем (адаптируем)
│   ├── payments.py          # ✅ Платежные сообщения (сохраняем)
│   ├── errors.py            # ✅ Сообщения об ошибках (расширяем)
│   ├── reputation.py        # ➕ Анализ репутации (новый)
│   ├── deepfake.py          # ➕ Детекция дипфейков (новый)
│   ├── kyc.py               # ➕ KYC верификация (новый)
│   ├── security.py          # ➕ Кибербезопасность (новый)
│   └── reports.py           # ✅ Отчеты (адаптируем)
└── ru/                       # Русские переводы (зеркальная структура)
```

## 🔄 Адаптация существующих модулей

### 1. welcome.py - Приветственные сообщения

#### Английский (en/welcome.py)
```python
"""
Welcome messages for AIDI.APP - Reputation and KYC service
"""

# Первое приветствие
welcome_first_time = """
🛡️ Welcome to AIDI.APP!

Your AI-powered reputation analysis and deepfake detection service.

🔍 **Reputation Analysis** - Comprehensive digital footprint assessment
🎭 **Deepfake Detection** - Advanced AI-powered media verification  
🔐 **KYC Verification** - Know Your Customer identity validation

Choose your language to get started:
"""

welcome_returning_user = """
🛡️ Welcome back to AIDI.APP!

Ready to analyze reputation or detect deepfakes?

💳 Your balance: {credits} credits
📊 Analyses completed: {total_analyses}
⭐ Your reputation score: {user_reputation}/100
"""

# Выбор языка
language_selection = "🌐 Please select your language:"
language_changed = "✅ Language changed to English"

# Основное меню
main_menu_title = "🛡️ AIDI.APP - Main Menu"
main_menu_subtitle = "Choose the service you need:"

# Кнопки главного меню
btn_reputation_analysis = "🔍 Reputation Analysis"
btn_deepfake_detection = "🎭 Deepfake Detection"
btn_profile = "👤 Profile"
btn_buy_credits = "💳 Buy Credits"
btn_history = "📊 Analysis History"
btn_help = "❓ Help"
btn_settings = "⚙️ Settings"

# Статистика пользователя
user_stats = """
📊 **Your Statistics:**
• Reputation analyses: {reputation_count}
• Deepfake detections: {deepfake_count}
• KYC verifications: {kyc_count}
• Credits remaining: {credits}
• Member since: {registration_date}
"""
```

#### Русский (ru/welcome.py)
```python
"""
Приветственные сообщения для AIDI.APP - сервис репутации и KYC
"""

# Первое приветствие
welcome_first_time = """
🛡️ Добро пожаловать в AIDI.APP!

Ваш ИИ-сервис анализа репутации и детекции дипфейков.

🔍 **Анализ репутации** - Комплексная оценка цифрового следа
🎭 **Детекция дипфейков** - Продвинутая ИИ-проверка медиафайлов
🔐 **KYC верификация** - Проверка личности "Знай своего клиента"

Выберите язык для начала работы:
"""

welcome_returning_user = """
🛡️ С возвращением в AIDI.APP!

Готовы анализировать репутацию или проверять дипфейки?

💳 Ваш баланс: {credits} кредитов
📊 Анализов выполнено: {total_analyses}
⭐ Ваш рейтинг репутации: {user_reputation}/100
"""

# Выбор языка
language_selection = "🌐 Пожалуйста, выберите язык:"
language_changed = "✅ Язык изменен на русский"

# Основное меню
main_menu_title = "🛡️ AIDI.APP - Главное меню"
main_menu_subtitle = "Выберите нужный сервис:"

# Кнопки главного меню
btn_reputation_analysis = "🔍 Анализ репутации"
btn_deepfake_detection = "🎭 Проверка дипфейка"
btn_profile = "👤 Профиль"
btn_buy_credits = "💳 Купить кредиты"
btn_history = "📊 История анализов"
btn_help = "❓ Помощь"
btn_settings = "⚙️ Настройки"

# Статистика пользователя
user_stats = """
📊 **Ваша статистика:**
• Анализов репутации: {reputation_count}
• Проверок дипфейков: {deepfake_count}
• KYC верификаций: {kyc_count}
• Кредитов осталось: {credits}
• Пользователь с: {registration_date}
"""
```

### 2. help.py - Справочная информация

#### Английский (en/help.py)
```python
"""
Help and FAQ for AIDI.APP
"""

# Основная справка
help_main = """
🛡️ **AIDI.APP Help Center**

**What is AIDI.APP?**
AI-powered service for reputation analysis and deepfake detection through Telegram.

**Main Features:**
🔍 **Reputation Analysis** - Analyze digital footprint and reputation
🎭 **Deepfake Detection** - Detect AI-generated fake media
🔐 **KYC Verification** - Identity verification services

**How it works:**
1. Choose analysis type
2. Provide required data (name, photo, media file)
3. Get AI-powered results in 30-60 seconds
4. Download detailed reports

**Credit System:**
• 1 credit = 1 basic analysis
• 2 credits = 1 extended analysis
• 3 credits = 1 deep analysis or KYC verification

Need more help? Contact support: @AIDISupport
"""

# FAQ
faq_reputation = """
❓ **Reputation Analysis FAQ**

**Q: What data sources do you check?**
A: Social media, public records, news mentions, court records, professional networks.

**Q: How accurate is the analysis?**
A: Our AI achieves 90%+ accuracy using advanced algorithms and multiple data sources.

**Q: How long does analysis take?**
A: Basic analysis: 30-60 seconds, Extended: 2-5 minutes, Deep: 5-15 minutes.

**Q: Is my data secure?**
A: Yes, we use encryption and automatically delete data after 30 days (GDPR compliant).

**Q: Can I analyze myself?**
A: Yes, self-analysis helps you understand your digital reputation.
"""

faq_deepfake = """
❓ **Deepfake Detection FAQ**

**Q: What media types can you analyze?**
A: Images (JPG, PNG), Videos (MP4, AVI, MOV), Audio files (MP3, WAV).

**Q: How do you detect deepfakes?**
A: We use multiple AI models analyzing facial inconsistencies, temporal artifacts, and compression patterns.

**Q: What's the detection accuracy?**
A: 95%+ accuracy for high-quality deepfakes, 85%+ for sophisticated ones.

**Q: File size limits?**
A: Images: up to 50MB, Videos: up to 500MB, Audio: up to 100MB.

**Q: How long does detection take?**
A: Quick scan: 15-30 seconds, Detailed analysis: 1-3 minutes.
"""

# Команды бота
bot_commands = """
🤖 **Bot Commands**

/start - Start or restart the bot
/help - Show this help message
/profile - View your profile and settings
/balance - Check your credit balance
/history - View analysis history
/settings - Change bot settings
/language - Change language
/support - Contact support team

**Quick Actions:**
• Send photo → Start reputation analysis
• Send video → Start deepfake detection
• Type name/phone → Search reputation
"""
```

#### Русский (ru/help.py)
```python
"""
Справка и FAQ для AIDI.APP
"""

# Основная справка
help_main = """
🛡️ **Центр помощи AIDI.APP**

**Что такое AIDI.APP?**
ИИ-сервис анализа репутации и детекции дипфейков через Telegram.

**Основные функции:**
🔍 **Анализ репутации** - Анализ цифрового следа и репутации
🎭 **Детекция дипфейков** - Обнаружение ИИ-сгенерированных фейков
🔐 **KYC верификация** - Услуги проверки личности

**Как это работает:**
1. Выберите тип анализа
2. Предоставьте необходимые данные (имя, фото, медиафайл)
3. Получите ИИ-результаты за 30-60 секунд
4. Скачайте подробные отчеты

**Система кредитов:**
• 1 кредит = 1 базовый анализ
• 2 кредита = 1 расширенный анализ
• 3 кредита = 1 глубокий анализ или KYC верификация

Нужна помощь? Обратитесь в поддержку: @AIDISupport
"""

# FAQ
faq_reputation = """
❓ **FAQ по анализу репутации**

**В: Какие источники данных вы проверяете?**
О: Социальные сети, публичные реестры, упоминания в СМИ, судебные записи, профессиональные сети.

**В: Насколько точен анализ?**
О: Наш ИИ достигает точности 90%+ используя продвинутые алгоритмы и множественные источники данных.

**В: Сколько времени занимает анализ?**
О: Базовый анализ: 30-60 секунд, Расширенный: 2-5 минут, Глубокий: 5-15 минут.

**В: Безопасны ли мои данные?**
О: Да, мы используем шифрование и автоматически удаляем данные через 30 дней (соответствие GDPR).

**В: Могу ли я анализировать себя?**
О: Да, самоанализ поможет понять вашу цифровую репутацию.
"""

faq_deepfake = """
❓ **FAQ по детекции дипфейков**

**В: Какие типы медиа вы можете анализировать?**
О: Изображения (JPG, PNG), Видео (MP4, AVI, MOV), Аудиофайлы (MP3, WAV).

**В: Как вы обнаруживаете дипфейки?**
О: Мы используем множественные ИИ-модели, анализирующие лицевые несоответствия, временные артефакты и паттерны сжатия.

**В: Какова точность обнаружения?**
О: 95%+ точность для высококачественных дипфейков, 85%+ для сложных.

**В: Ограничения размера файлов?**
О: Изображения: до 50МБ, Видео: до 500МБ, Аудио: до 100МБ.

**В: Сколько времени занимает обнаружение?**
О: Быстрое сканирование: 15-30 секунд, Детальный анализ: 1-3 минуты.
"""

# Команды бота
bot_commands = """
🤖 **Команды бота**

/start - Запустить или перезапустить бота
/help - Показать это сообщение помощи
/profile - Посмотреть профиль и настройки
/balance - Проверить баланс кредитов
/history - Посмотреть историю анализов
/settings - Изменить настройки бота
/language - Изменить язык
/support - Связаться с поддержкой

**Быстрые действия:**
• Отправить фото → Начать анализ репутации
• Отправить видео → Начать детекцию дипфейка
• Ввести имя/телефон → Поиск репутации
"""
```

## ➕ Новые модули переводов

### 3. reputation.py - Анализ репутации

#### Английский (en/reputation.py)
```python
"""
Reputation analysis messages for AIDI.APP
"""

# Заголовки и меню
reputation_title = "🔍 Reputation Analysis"
reputation_subtitle = "Comprehensive digital footprint assessment"

# Кнопки меню репутации
btn_basic_analysis = "⚡ Basic Analysis (1 credit)"
btn_extended_analysis = "🔬 Extended Analysis (2 credits)"
btn_deep_analysis = "🕵️ Deep Analysis (3 credits)"
btn_back_to_main = "⬅️ Back to Main Menu"
btn_new_analysis = "🔄 New Analysis"

# Ввод данных
input_prompt = """
🔍 **Reputation Analysis Setup**

Please provide information about the person you want to analyze:

**Required (at least one):**
• Full name
• Phone number
• Email address
• Photo

**Optional:**
• Social media profiles
• Additional information

Choose how to provide the data:
"""

btn_enter_name = "📝 Enter Name"
btn_enter_phone = "📞 Enter Phone"
btn_enter_email = "📧 Enter Email"
btn_upload_photo = "📷 Upload Photo"
btn_social_profiles = "🌐 Social Profiles"
btn_start_analysis = "🚀 Start Analysis"
btn_clear_data = "🗑️ Clear Data"

# Промпты для ввода
prompt_name = "👤 Please enter the full name of the person:"
prompt_phone = "📞 Please enter the phone number (with country code):"
prompt_email = "📧 Please enter the email address:"
prompt_photo = "📷 Please upload a photo of the person:"
prompt_social = "🌐 Please provide social media profiles (one per line):"

# Валидация данных
validation_name_invalid = "❌ Please enter a valid full name (at least 2 words)"
validation_phone_invalid = "❌ Please enter a valid phone number with country code"
validation_email_invalid = "❌ Please enter a valid email address"
validation_photo_invalid = "❌ Please upload a valid photo (JPG, PNG, max 50MB)"
validation_insufficient_data = "❌ Please provide at least name, phone, email, or photo"

# Подтверждение анализа
analysis_confirmation = """
✅ **Analysis Data Confirmed**

**Target Information:**
• Name: {name}
• Phone: {phone}
• Email: {email}
• Photo: {photo_status}
• Social profiles: {social_count}

**Analysis Type:** {analysis_type}
**Cost:** {credits} credits
**Estimated time:** {estimated_time}

Proceed with analysis?
"""

btn_confirm_analysis = "✅ Confirm & Start"
btn_edit_data = "✏️ Edit Data"

# Процесс анализа
analysis_started = """
🚀 **Analysis Started**

Your reputation analysis is now in progress...

**Current stage:** {stage}
**Progress:** {progress}%
**Estimated completion:** {eta}

You'll be notified when the analysis is complete.
"""

analysis_progress_stages = {
    "initializing": "Initializing analysis...",
    "data_collection": "Collecting data from sources...",
    "social_media_scan": "Scanning social media profiles...",
    "public_records_check": "Checking public records...",
    "news_search": "Searching news mentions...",
    "ai_analysis": "AI analysis in progress...",
    "report_generation": "Generating detailed report...",
    "finalizing": "Finalizing results..."
}

# Результаты анализа
analysis_completed = """
✅ **Analysis Completed**

**Target:** {target_name}
**Analysis Type:** {analysis_type}
**Completion Time:** {completion_time}

**Key Scores:**
🎯 Risk Score: {risk_score}/100
⭐ Credibility: {credibility_score}/100
📊 Activity Level: {activity_score}/100
💭 Sentiment: {sentiment_description}

**Summary:**
{executive_summary}

**Sources Found:** {sources_count}
**Red Flags:** {red_flags_count}
**Positive Indicators:** {positive_indicators_count}
"""

btn_view_full_report = "📋 View Full Report"
btn_download_pdf = "📄 Download PDF"
btn_share_report = "📤 Share Report"

# Описания скоров
risk_score_descriptions = {
    "low": "Low Risk (0-30) - Minimal reputation concerns",
    "moderate": "Moderate Risk (31-60) - Some concerns identified",
    "high": "High Risk (61-85) - Significant reputation issues",
    "critical": "Critical Risk (86-100) - Severe reputation problems"
}

sentiment_descriptions = {
    "very_positive": "Very Positive (0.6 to 1.0)",
    "positive": "Positive (0.2 to 0.6)",
    "neutral": "Neutral (-0.2 to 0.2)",
    "negative": "Negative (-0.6 to -0.2)",
    "very_negative": "Very Negative (-1.0 to -0.6)"
}

# Ошибки анализа
analysis_failed = """
❌ **Analysis Failed**

Unfortunately, we couldn't complete the reputation analysis.

**Error:** {error_message}
**Possible reasons:**
• Insufficient data provided
• Target person not found in available sources
• Technical issues with data sources
• Analysis timeout

Your credits have been refunded.
"""

analysis_timeout = """
⏰ **Analysis Timeout**

The analysis is taking longer than expected.

**Options:**
• Wait for completion (you'll be notified)
• Cancel and get refund
• Try with different data

Current progress: {progress}%
"""

btn_wait_completion = "⏳ Wait for Completion"
btn_cancel_refund = "❌ Cancel & Refund"

# Детальный отчет
detailed_report_header = """
📋 **Detailed Reputation Report**

**Target:** {target_name}
**Analysis Date:** {analysis_date}
**Report ID:** {report_id}

═══════════════════════════
"""

report_section_overview = "📊 **OVERVIEW**"
report_section_scores = "🎯 **SCORES & METRICS**"
report_section_sources = "🔍 **DATA SOURCES**"
report_section_findings = "📝 **KEY FINDINGS**"
report_section_recommendations = "💡 **RECOMMENDATIONS**"
report_section_timeline = "📅 **ACTIVITY TIMELINE**"

# История анализов
history_title = "📊 Reputation Analysis History"
history_empty = "📭 No reputation analyses yet. Start your first analysis!"

history_item = """
🔍 **{target_name}**
📅 {date} | ⏱️ {duration}
🎯 Risk: {risk_score}/100 | ⭐ Credibility: {credibility_score}/100
📊 {sources_count} sources | 💳 {credits_used} credits
"""

btn_view_analysis = "👁️ View"
btn_reanalyze = "🔄 Re-analyze"
btn_delete_analysis = "🗑️ Delete"
```

#### Русский (ru/reputation.py)
```python
"""
Сообщения анализа репутации для AIDI.APP
"""

# Заголовки и меню
reputation_title = "🔍 Анализ репутации"
reputation_subtitle = "Комплексная оценка цифрового следа"

# Кнопки меню репутации
btn_basic_analysis = "⚡ Базовый анализ (1 кредит)"
btn_extended_analysis = "🔬 Расширенный анализ (2 кредита)"
btn_deep_analysis = "🕵️ Глубокий анализ (3 кредита)"
btn_back_to_main = "⬅️ Главное меню"
btn_new_analysis = "🔄 Новый анализ"

# Ввод данных
input_prompt = """
🔍 **Настройка анализа репутации**

Пожалуйста, предоставьте информацию о человеке, которого хотите проанализировать:

**Обязательно (минимум одно):**
• Полное имя
• Номер телефона
• Email адрес
• Фотография

**Опционально:**
• Профили в соцсетях
• Дополнительная информация

Выберите способ предоставления данных:
"""

btn_enter_name = "📝 Ввести имя"
btn_enter_phone = "📞 Ввести телефон"
btn_enter_email = "📧 Ввести email"
btn_upload_photo = "📷 Загрузить фото"
btn_social_profiles = "🌐 Соцсети"
btn_start_analysis = "🚀 Начать анализ"
btn_clear_data = "🗑️ Очистить данные"

# Промпты для ввода
prompt_name = "👤 Пожалуйста, введите полное имя человека:"
prompt_phone = "📞 Пожалуйста, введите номер телефона (с кодом страны):"
prompt_email = "📧 Пожалуйста, введите email адрес:"
prompt_photo = "📷 Пожалуйста, загрузите фотографию человека:"
prompt_social = "🌐 Пожалуйста, укажите профили в соцсетях (по одному на строку):"

# Валидация данных
validation_name_invalid = "❌ Пожалуйста, введите корректное полное имя (минимум 2 слова)"
validation_phone_invalid = "❌ Пожалуйста, введите корректный номер телефона с кодом страны"
validation_email_invalid = "❌ Пожалуйста, введите корректный email адрес"
validation_photo_invalid = "❌ Пожалуйста, загрузите корректное фото (JPG, PNG, макс 50МБ)"
validation_insufficient_data = "❌ Пожалуйста, предоставьте минимум имя, телефон, email или фото"

# Подтверждение анализа
analysis_confirmation = """
✅ **Данные для анализа подтверждены**

**Информация о цели:**
• Имя: {name}
• Телефон: {phone}
• Email: {email}
• Фото: {photo_status}
• Профили в соцсетях: {social_count}

**Тип анализа:** {analysis_type}
**Стоимость:** {credits} кредитов
**Примерное время:** {estimated_time}

Продолжить анализ?
"""

btn_confirm_analysis = "✅ Подтвердить и начать"
btn_edit_data = "✏️ Редактировать данные"

# Процесс анализа
analysis_started = """
🚀 **Анализ запущен**

Ваш анализ репутации сейчас выполняется...

**Текущий этап:** {stage}
**Прогресс:** {progress}%
**Примерное завершение:** {eta}

Вы получите уведомление по завершении анализа.
"""

analysis_progress_stages = {
    "initializing": "Инициализация анализа...",
    "data_collection": "Сбор данных из источников...",
    "social_media_scan": "Сканирование профилей в соцсетях...",
    "public_records_check": "Проверка публичных реестров...",
    "news_search": "Поиск упоминаний в СМИ...",
    "ai_analysis": "ИИ-анализ в процессе...",
    "report_generation": "Генерация подробного отчета...",
    "finalizing": "Финализация результатов..."
}

# Результаты анализа
analysis_completed = """
✅ **Анализ завершен**

**Цель:** {target_name}
**Тип анализа:** {analysis_type}
**Время завершения:** {completion_time}

**Ключевые показатели:**
🎯 Риск-скор: {risk_score}/100
⭐ Достоверность: {credibility_score}/100
📊 Уровень активности: {activity_score}/100
💭 Тональность: {sentiment_description}

**Резюме:**
{executive_summary}

**Найдено источников:** {sources_count}
**Красные флаги:** {red_flags_count}
**Позитивные индикаторы:** {positive_indicators_count}
"""

btn_view_full_report = "📋 Полный отчет"
btn_download_pdf = "📄 Скачать PDF"
btn_share_report = "📤 Поделиться отчетом"

# Описания скоров
risk_score_descriptions = {
    "low": "Низкий риск (0-30) - Минимальные репутационные проблемы",
    "moderate": "Умеренный риск (31-60) - Выявлены некоторые проблемы",
    "high": "Высокий риск (61-85) - Значительные репутационные проблемы",
    "critical": "Критический риск (86-100) - Серьезные репутационные проблемы"
}

sentiment_descriptions = {
    "very_positive": "Очень позитивная (0.6 до 1.0)",
    "positive": "Позитивная (0.2 до 0.6)",
    "neutral": "Нейтральная (-0.2 до 0.2)",
    "negative": "Негативная (-0.6 до -0.2)",
    "very_negative": "Очень негативная (-1.0 до -0.6)"
}

# Ошибки анализа
analysis_failed = """
❌ **Анализ не удался**

К сожалению, мы не смогли завершить анализ репутации.

**Ошибка:** {error_message}
**Возможные причины:**
• Недостаточно предоставленных данных
• Целевое лицо не найдено в доступных источниках
• Технические проблемы с источниками данных
• Превышено время анализа

Ваши кредиты возвращены.
"""

analysis_timeout = """
⏰ **Превышено время анализа**

Анализ занимает больше времени, чем ожидалось.

**Варианты:**
• Дождаться завершения (вы получите уведомление)
• Отменить и получить возврат
• Попробовать с другими данными

Текущий прогресс: {progress}%
"""

btn_wait_completion = "⏳ Дождаться завершения"
btn_cancel_refund = "❌ Отменить и вернуть кредиты"
```

### 4. deepfake.py - Детекция дипфейков

#### Английский (en/deepfake.py)
```python
"""
Deepfake detection messages for AIDI.APP
"""

# Заголовки и меню
deepfake_title = "🎭 Deepfake Detection"
deepfake_subtitle = "AI-powered media authenticity verification"

# Кнопки меню дипфейков
btn_quick_scan = "⚡ Quick Scan (1 credit)"
btn_detailed_