-- ==========================================
-- ROLLBACK для МИГРАЦИИ v0.4.2 - ОГРАНИЧЕНИЯ БД
-- ==========================================
-- Date: 2025-01-21
-- Purpose: Rollback database constraints and optimizations
-- Rollback for: 2025-01-21_constraints.sql

-- Удалить новые индексы
DROP INDEX IF EXISTS idx_users_telegram_id_unique;
DROP INDEX IF EXISTS idx_users_created_at;
DROP INDEX IF EXISTS idx_users_credits_remaining;
DROP INDEX IF EXISTS idx_users_total_paid;
DROP INDEX IF EXISTS idx_logs_timestamp_desc;
DROP INDEX IF EXISTS idx_logs_user_timestamp;
DROP INDEX IF EXISTS idx_logs_action_type_timestamp;
DROP INDEX IF EXISTS idx_payments_user_id;
DROP INDEX IF EXISTS idx_payments_status;
DROP INDEX IF EXISTS idx_payments_created_at;
DROP INDEX IF EXISTS idx_payments_amount;

-- Удалить ограничения (constraints)
ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_users_credits_non_negative;
ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_users_total_paid_non_negative;
ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_users_telegram_id_positive;

ALTER TABLE logs DROP CONSTRAINT IF EXISTS chk_logs_action_type_valid;

ALTER TABLE payments DROP CONSTRAINT IF EXISTS chk_payments_amount_positive;
ALTER TABLE payments DROP CONSTRAINT IF EXISTS chk_payments_status_valid;

-- Удалить уникальные ограничения
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_telegram_id_unique;

-- Удалить внешние ключи (если они были добавлены)
ALTER TABLE logs DROP CONSTRAINT IF EXISTS fk_logs_user_id;
ALTER TABLE payments DROP CONSTRAINT IF EXISTS fk_payments_user_id;
ALTER TABLE user_profiles DROP CONSTRAINT IF EXISTS fk_user_profiles_user_id;

-- Удалить NOT NULL ограничения (осторожно - может привести к проблемам)
-- ALTER TABLE users ALTER COLUMN telegram_id DROP NOT NULL;
-- ALTER TABLE users ALTER COLUMN created_at DROP NOT NULL;

-- Удалить комментарии к таблицам и столбцам
COMMENT ON TABLE users IS NULL;
COMMENT ON TABLE logs IS NULL;
COMMENT ON TABLE payments IS NULL;
COMMENT ON TABLE user_profiles IS NULL;

COMMENT ON COLUMN users.telegram_id IS NULL;
COMMENT ON COLUMN users.credits_remaining IS NULL;
COMMENT ON COLUMN users.total_paid IS NULL;
COMMENT ON COLUMN users.created_at IS NULL;
COMMENT ON COLUMN users.subscription_type IS NULL;
COMMENT ON COLUMN users.subscription_expires_at IS NULL;

COMMENT ON COLUMN logs.user_id IS NULL;
COMMENT ON COLUMN logs.action_type IS NULL;
COMMENT ON COLUMN logs.timestamp IS NULL;
COMMENT ON COLUMN logs.details IS NULL;

COMMENT ON COLUMN payments.user_id IS NULL;
COMMENT ON COLUMN payments.amount IS NULL;
COMMENT ON COLUMN payments.status IS NULL;
COMMENT ON COLUMN payments.payment_method IS NULL;
COMMENT ON COLUMN payments.external_id IS NULL;
COMMENT ON COLUMN payments.created_at IS NULL;

-- Примечание: Этот rollback удаляет оптимизации производительности
-- Рекомендуется тщательно протестировать после выполнения rollback