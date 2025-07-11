-- ==========================================
-- ФИНАЛЬНАЯ МИГРАЦИЯ v0.4.1  
-- ==========================================
-- Date: 2025-01-20
-- Approved by: User

-- ==========================================
-- 1. СОЗДАТЬ ТАБЛИЦУ ПРОФИЛЕЙ ПОЛЬЗОВАТЕЛЕЙ
-- ==========================================

-- Создать таблицу профилей пользователей
CREATE TABLE user_profiles (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES users(id) UNIQUE NOT NULL,
    age INTEGER CHECK (age BETWEEN 10 AND 120),
    gender TEXT CHECK (gender IN ('male', 'female')),
    height_cm INTEGER CHECK (height_cm BETWEEN 100 AND 250),
    weight_kg NUMERIC(5,2) CHECK (weight_kg BETWEEN 30 AND 300),
    activity_level TEXT CHECK (activity_level IN ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active')),
    goal TEXT CHECK (goal IN ('lose_weight', 'maintain_weight', 'gain_weight')),
    daily_calories_target INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- ==========================================
-- 2. РАСШИРИТЬ ТАБЛИЦУ LOGS ДЛЯ ЛОГИРОВАНИЯ
-- ==========================================

-- Добавить action_type для различных действий пользователей
ALTER TABLE logs ADD COLUMN IF NOT EXISTS action_type TEXT DEFAULT 'photo_analysis';

-- Сделать photo_url и kbzhu nullable для поддержки не-фото действий
ALTER TABLE logs ALTER COLUMN photo_url DROP NOT NULL;
ALTER TABLE logs ALTER COLUMN kbzhu DROP NOT NULL;

-- Добавить metadata для дополнительных данных действий
ALTER TABLE logs ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- ==========================================
-- 3. СОЗДАТЬ ИНДЕКСЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ
-- ==========================================

CREATE INDEX IF NOT EXISTS idx_logs_action_type ON logs(action_type);
CREATE INDEX IF NOT EXISTS idx_logs_user_action_time ON logs(user_id, action_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);

-- ==========================================
-- 4. СОЗДАТЬ ТРИГГЕР ДЛЯ UPDATED_AT
-- ==========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ==========================================
-- 5. СОЗДАТЬ VIEWS ДЛЯ АНАЛИТИКИ
-- ==========================================

-- View для сводки активности пользователей
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT 
    u.telegram_id,
    u.credits_remaining,
    u.total_paid,
    u.created_at,
    COUNT(l.id) as total_actions,
    COUNT(CASE WHEN l.action_type = 'photo_analysis' THEN 1 END) as photo_analyses,
    COUNT(CASE WHEN l.action_type = 'start' THEN 1 END) as start_commands,
    COUNT(CASE WHEN l.action_type = 'help' THEN 1 END) as help_commands,
    COUNT(CASE WHEN l.action_type = 'status' THEN 1 END) as status_commands,
    COUNT(CASE WHEN l.action_type = 'buy' THEN 1 END) as buy_commands,
    MAX(l.timestamp) as last_activity
FROM users u
LEFT JOIN logs l ON u.id = l.user_id
GROUP BY u.id, u.telegram_id, u.credits_remaining, u.total_paid, u.created_at;

-- View для отслеживания дневных калорий
CREATE OR REPLACE VIEW daily_calories_tracking AS
SELECT 
    u.telegram_id,
    up.daily_calories_target,
    DATE(l.timestamp) as date,
    SUM(CAST(l.kbzhu->>'calories' AS NUMERIC)) as consumed_calories,
    up.daily_calories_target - SUM(CAST(l.kbzhu->>'calories' AS NUMERIC)) as remaining_calories
FROM users u
JOIN user_profiles up ON u.id = up.user_id
LEFT JOIN logs l ON u.id = l.user_id 
WHERE l.action_type = 'photo_analysis' 
  AND l.kbzhu IS NOT NULL
  AND up.daily_calories_target IS NOT NULL
GROUP BY u.telegram_id, up.daily_calories_target, DATE(l.timestamp);

-- ==========================================
-- 6. ДОБАВИТЬ КОММЕНТАРИИ ДЛЯ ДОКУМЕНТАЦИИ
-- ==========================================

COMMENT ON TABLE user_profiles IS 'User personal data for calorie calculation';
COMMENT ON COLUMN user_profiles.daily_calories_target IS 'Calculated daily calorie target based on profile data';
COMMENT ON COLUMN logs.action_type IS 'Type of user action: photo_analysis, start, help, status, buy, profile, daily';
COMMENT ON COLUMN logs.metadata IS 'Additional action data in JSON format'; 