-- ==========================================
-- МИГРАЦИЯ v0.4.2 - МУЛЬТИЯЗЫЧНОСТЬ
-- ==========================================
-- Date: 2025-01-21
-- Purpose: Add multilingual support to users table
-- Depends on: v0.4.1 (user_profiles)

-- Добавить поддержку языка в таблицу users
ALTER TABLE users ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'en' CHECK (language IN ('en', 'ru'));
ALTER TABLE users ADD COLUMN IF NOT EXISTS country TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number TEXT;

-- Создать индекс для быстрого поиска по языку
CREATE INDEX IF NOT EXISTS idx_users_language ON users(language);

-- Добавить комментарии для новых полей
COMMENT ON COLUMN users.language IS 'User preferred language: en (English) or ru (Russian)';
COMMENT ON COLUMN users.country IS 'User country code for language detection';
COMMENT ON COLUMN users.phone_number IS 'User phone number for language detection';

-- Обновить view для включения информации о языке
-- Сначала удаляем существующий view, затем создаем новый
DROP VIEW IF EXISTS user_activity_summary;
CREATE VIEW user_activity_summary AS
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