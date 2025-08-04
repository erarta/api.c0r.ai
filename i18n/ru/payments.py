# Russian translations for payment messages and credit management
TRANSLATIONS = {
    # Status messages
    "status_title": "📊 *Твой Потрясающий Статус Аккаунта*",
    "status_user_id": "🆔 Твой ID: `{user_id}`",
    "status_credits": "💳 Кредитов у тебя осталось: *{credits}*",
    "status_total_paid": "💰 Всего ты инвестировал в свое здоровье: *{total_paid:.2f} Р*",
    "status_member_since": "📅 Ты со мной с: `{date}`",
    "status_system": "🤖 Система: *c0r.ai v{version}*",
    "status_online": "🌐 Статус: *Онлайн и готов помочь тебе!*",
    "status_powered_by": "⚡ Работает на c0R AI Vision - специально для тебя!",
    
    # Payment plans and invoices
    "plan_basic_title": "Базовый план",
    "plan_basic_description": "20 кредитов для анализа еды",
    "plan_pro_title": "Про план",
    "plan_pro_description": "100 кредитов для анализа еды",
    "invoice_credits_label": "{credits} кредитов",
    "invoice_payment_error": "❌ Ошибка платежной системы. Пожалуйста, обратитесь в поддержку.",
    "invoice_invalid_plan": "❌ Выбран неверный план платежа.",
    "invoice_created": "✅ Инвойс создан для пользователя {user_id}, план {plan_id}",
    "invoice_failed": "❌ Не удалось создать инвойс: {error}",
    
    # Payment messages
    "payment_title": "💳 **Давай получим тебе больше кредитов!**",
    "payment_description": "Выбери план, который лучше всего подходит для твоего потрясающего путешествия к здоровью:",
    "payment_basic_title": "Базовый план - Идеальный старт!",
    "payment_basic_desc": "20 кредитов для анализа твоей вкусной еды",
    "payment_pro_title": "Про план - Для целеустремленных!",
    "payment_pro_desc": "100 кредитов для твоего путешествия к здоровью",
    "payment_price": "{price} Р",
    "payment_credits": "{credits} кредитов",
    
    # Buy command messages
    "buy_credits_title": "Давай получим тебе больше кредитов!",
    "current_credits": "У тебя сейчас есть",
    "basic_plan_title": "Базовый план - Отличный выбор!",
    "pro_plan_title": "Про план - Превосходная ценность!",
    "credits": "кредитов",
    "rubles": "Р",
    "for": "за",
    "choose_plan_to_continue": "Выбери план, который тебе подходит",
    "credits_explanation": "💡 **Что такое кредиты?**\n• 1 кредит = 1 анализ фото\n• Каждое фото еды, которое ты отправляешь, стоит 1 кредит\n• Твои кредиты никогда не истекают - они твои навсегда!",
    "basic_plan_btn": "Базовый план ({price} Р) - Начнем!",
    "pro_plan_btn": "Про план ({price} Р) - Я готов!",
    
    # Buy credits translations
    "buy_credits_title": "💳 Давай получим тебе больше кредитов!",
    "buy_credits_current": "У тебя сейчас: {credits} кредитов",
    "buy_credits_what_are": "💡 Что такое кредиты?",
    "buy_credits_explanation": "• 1 кредит = 1 анализ фото еды\n• Каждое фото еды, которое ты отправляешь, стоит 1 кредит\n• Твои кредиты никогда не истекают - они твои навсегда!",
    "buy_credits_basic": "Базовый план ({price} Р) - Отличный старт!",
    "buy_credits_pro": "Про план ({price} Р) - Превосходная ценность!",
    "buy_credits_choose": "Выбери план, который тебе подходит:",
    
    # Payment success messages
    "payment_success_title": "🎉 **Платеж успешно завершен!**",
    "payment_success_message": "Спасибо за твой платеж! Твои кредиты уже добавлены к твоему аккаунту.",
    "payment_success_credits_added": "✅ Добавлено {credits} кредитов к твоему аккаунту",
    "payment_success_total_credits": "💳 Теперь у тебя {total_credits} кредитов",
    "payment_success_continue": "Продолжай отправлять фото еды для анализа!",
    
    # Payment error messages
    "payment_error_title": "❌ **Ошибка платежа**",
    "payment_error_message": "К сожалению, произошла ошибка при обработке твоего платежа.",
    "payment_error_contact_support": "Пожалуйста, обратись в поддержку, если проблема повторится.",
    
    # Pre-checkout messages
    "pre_checkout_title": "🔍 **Проверка платежа**",
    "pre_checkout_message": "Проверяем детали твоего платежа...",
    "pre_checkout_success": "✅ Платеж одобрен!",
    "pre_checkout_error": "❌ Ошибка проверки платежа",
    
    # Back button
    "btn_back": "Назад",
    
    # Payment processing messages
    "payment_processing": "⏳ Обрабатываем твой платеж...",
    "payment_verifying": "🔍 Проверяем платеж...",
    "payment_completed": "✅ Платеж завершен успешно!",
    "payment_failed": "❌ Платеж не удался",
    
    # Credit management
    "credits_remaining": "Кредитов осталось: {credits}",
    "credits_used": "Использовано кредитов: {credits}",
    "credits_added": "Добавлено кредитов: {credits}",
    "credits_total": "Всего кредитов: {credits}",
    
    # Payment provider messages
    "provider_yookassa": "YooKassa",
    "provider_stripe": "Stripe",
    "provider_telegram": "Telegram Payments",
    
    # Currency
    "currency_rub": "Р",
    "currency_usd": "$",
    "currency_eur": "€",
    
    # Time periods
    "period_month": "месяц",
    "period_year": "год",
    "period_week": "неделя",
    "period_day": "день",
    
    # Payment status
    "status_pending": "Ожидает оплаты",
    "status_paid": "Оплачено",
    "status_cancelled": "Отменено",
    "status_expired": "Истекло",
    "status_refunded": "Возвращено",
    "status_failed": "Не удалось",
    
    # Payment confirmation
    "confirm_payment": "Подтвердить платеж",
    "cancel_payment": "Отменить платеж",
    "payment_confirmed": "Платеж подтвержден",
    "payment_cancelled": "Платеж отменен",
    
    # Support messages
    "contact_support": "Обратиться в поддержку",
    "support_message": "Если у тебя есть вопросы по платежам, пожалуйста, обратись в поддержку.",
    "support_email": "support@c0r.ai",
    "support_telegram": "@c0r_support",
}