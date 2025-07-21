-- ==========================================
-- ROLLBACK для МИГРАЦИИ v0.4.2 - МУЛЬТИЯЗЫЧНОСТЬ
-- ==========================================
-- Date: 2025-01-21
-- Purpose: Rollback multilingual support
-- Rollback for: 2025-01-21_multilingual.sql

-- Удалить view для активности пользователей (новая версия с языком)
DROP VIEW IF EXISTS user_activity_summary;

-- Восстановить исходный view без поддержки языка
CREATE VIEW user_activity_summary AS
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

-- Удалить индекс для языка
DROP INDEX IF EXISTS idx_users_language;

-- Удалить новые столбцы из таблицы users
ALTER TABLE users DROP COLUMN IF EXISTS language;
ALTER TABLE users DROP COLUMN IF EXISTS country;
ALTER TABLE users DROP COLUMN IF EXISTS phone_number;

-- Примечание: Этот rollback приведет к потере информации о языковых предпочтениях пользователей
-- Рекомендуется создать резервную копию данных перед выполнением rollback