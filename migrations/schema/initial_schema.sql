-- ==========================================
-- ПОЛНАЯ СХЕМА БАЗЫ ДАННЫХ c0r.AI
-- ==========================================
-- Version: v0.4.2
-- Date: 2025-01-21
-- Purpose: Complete database schema for fresh installations

-- ==========================================
-- ОСНОВНЫЕ ТАБЛИЦЫ
-- ==========================================

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL UNIQUE,
    credits_remaining INTEGER DEFAULT 0 CHECK (credits_remaining >= 0),
    total_paid INTEGER DEFAULT 0 CHECK (total_paid >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    subscription_type TEXT DEFAULT 'free' CHECK (subscription_type IN ('free', 'basic', 'premium')),
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    language TEXT DEFAULT 'en' CHECK (language IN ('en', 'ru')),
    country TEXT,
    phone_number TEXT,
    
    CONSTRAINT chk_users_telegram_id_positive CHECK (telegram_id > 0)
);

-- Таблица профилей пользователей
CREATE TABLE IF NOT EXISTS user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    telegram_id BIGINT NOT NULL,
    age INTEGER CHECK (age > 0 AND age < 150),
    weight REAL CHECK (weight > 0 AND weight < 1000),
    height REAL CHECK (height > 0 AND height < 300),
    gender TEXT CHECK (gender IN ('male', 'female')),
    activity_level TEXT DEFAULT 'moderate' CHECK (activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')),
    goal TEXT DEFAULT 'maintain' CHECK (goal IN ('lose', 'maintain', 'gain')),
    dietary_restrictions TEXT[],
    allergies TEXT[],
    preferred_cuisine TEXT[],
    daily_calorie_target INTEGER CHECK (daily_calorie_target > 0),
    bmr REAL CHECK (bmr > 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Таблица логов действий
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action_type TEXT NOT NULL CHECK (action_type IN (
        'start', 'help', 'status', 'buy', 'photo_analysis', 
        'recipe_generation', 'profile_update', 'calorie_calculation',
        'language_change'
    )),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    details JSONB
);

-- Таблица платежей
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL CHECK (amount > 0),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')),
    payment_method TEXT CHECK (payment_method IN ('yookassa', 'stripe')),
    external_id TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- ==========================================
-- ИНДЕКСЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ
-- ==========================================

-- Индексы для таблицы users
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_telegram_id_unique ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
CREATE INDEX IF NOT EXISTS idx_users_credits_remaining ON users(credits_remaining);
CREATE INDEX IF NOT EXISTS idx_users_total_paid ON users(total_paid);
CREATE INDEX IF NOT EXISTS idx_users_language ON users(language);

-- Индексы для таблицы user_profiles
CREATE INDEX IF NOT EXISTS idx_user_profiles_telegram_id ON user_profiles(telegram_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_updated_at ON user_profiles(updated_at);

-- Индексы для таблицы logs
CREATE INDEX IF NOT EXISTS idx_logs_user_action_timestamp ON logs(user_id, action_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_action_type ON logs(action_type);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp_desc ON logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_user_timestamp ON logs(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_action_type_timestamp ON logs(action_type, timestamp);

-- Индексы для таблицы payments
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);
CREATE INDEX IF NOT EXISTS idx_payments_amount ON payments(amount);

-- ==========================================
-- ПРЕДСТАВЛЕНИЯ (VIEWS)
-- ==========================================

-- Представление для сводки активности пользователей
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT 
    u.telegram_id,
    u.credits_remaining,
    u.total_paid,
    u.language,
    u.country,
    u.created_at,
    COUNT(l.id) as total_actions,
    COUNT(CASE WHEN l.action_type = 'photo_analysis' THEN 1 END) as photo_analyses,
    COUNT(CASE WHEN l.action_type = 'start' THEN 1 END) as start_commands,
    COUNT(CASE WHEN l.action_type = 'help' THEN 1 END) as help_commands,
    COUNT(CASE WHEN l.action_type = 'status' THEN 1 END) as status_commands,
    COUNT(CASE WHEN l.action_type = 'buy' THEN 1 END) as buy_commands,
    COUNT(CASE WHEN l.action_type = 'language_change' THEN 1 END) as language_changes,
    MAX(l.timestamp) as last_activity
FROM users u
LEFT JOIN logs l ON u.id = l.user_id
GROUP BY u.id, u.telegram_id, u.credits_remaining, u.total_paid, u.language, u.country, u.created_at;

-- ==========================================
-- ФУНКЦИИ
-- ==========================================

-- Функция для расчета базового метаболизма (BMR)
CREATE OR REPLACE FUNCTION calculate_bmr(age INTEGER, weight REAL, height REAL, gender TEXT)
RETURNS REAL AS $$
BEGIN
    IF gender = 'male' THEN
        RETURN 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age);
    ELSE
        RETURN 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Функция для расчета дневной нормы калорий
CREATE OR REPLACE FUNCTION calculate_daily_calories(age INTEGER, weight REAL, height REAL, gender TEXT, activity_level TEXT)
RETURNS REAL AS $$
DECLARE
    bmr REAL;
    activity_multiplier REAL;
BEGIN
    bmr := calculate_bmr(age, weight, height, gender);
    
    CASE activity_level
        WHEN 'sedentary' THEN activity_multiplier := 1.2;
        WHEN 'light' THEN activity_multiplier := 1.375;
        WHEN 'moderate' THEN activity_multiplier := 1.55;
        WHEN 'active' THEN activity_multiplier := 1.725;
        WHEN 'very_active' THEN activity_multiplier := 1.9;
        ELSE activity_multiplier := 1.55; -- default to moderate
    END CASE;
    
    RETURN bmr * activity_multiplier;
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- КОММЕНТАРИИ К ТАБЛИЦАМ И СТОЛБЦАМ
-- ==========================================

-- Комментарии к таблицам
COMMENT ON TABLE users IS 'Основная таблица пользователей Telegram бота';
COMMENT ON TABLE user_profiles IS 'Профили пользователей с персональными данными для расчета калорий';
COMMENT ON TABLE logs IS 'Логи действий пользователей в системе';
COMMENT ON TABLE payments IS 'История платежей и транзакций';

-- Комментарии к столбцам users
COMMENT ON COLUMN users.telegram_id IS 'Уникальный ID пользователя в Telegram';
COMMENT ON COLUMN users.credits_remaining IS 'Количество оставшихся кредитов для анализа фото';
COMMENT ON COLUMN users.total_paid IS 'Общая сумма платежей пользователя в копейках';
COMMENT ON COLUMN users.subscription_type IS 'Тип подписки: free, basic, premium';
COMMENT ON COLUMN users.language IS 'Предпочитаемый язык пользователя: en (English) или ru (Russian)';
COMMENT ON COLUMN users.country IS 'Код страны пользователя для определения языка';

-- Комментарии к столбцам user_profiles
COMMENT ON COLUMN user_profiles.daily_calorie_target IS 'Целевое количество калорий в день';
COMMENT ON COLUMN user_profiles.bmr IS 'Базовый метаболизм (Basal Metabolic Rate)';
COMMENT ON COLUMN user_profiles.activity_level IS 'Уровень физической активности';
COMMENT ON COLUMN user_profiles.goal IS 'Цель: похудение, поддержание веса, набор веса';

-- Комментарии к столбцам logs
COMMENT ON COLUMN logs.action_type IS 'Тип действия пользователя';
COMMENT ON COLUMN logs.details IS 'Дополнительные детали действия в формате JSON';

-- Комментарии к столбцам payments
COMMENT ON COLUMN payments.amount IS 'Сумма платежа в копейках';
COMMENT ON COLUMN payments.status IS 'Статус платежа: pending, completed, failed, cancelled';
COMMENT ON COLUMN payments.payment_method IS 'Метод платежа: yookassa, stripe';
COMMENT ON COLUMN payments.external_id IS 'ID платежа во внешней платежной системе';