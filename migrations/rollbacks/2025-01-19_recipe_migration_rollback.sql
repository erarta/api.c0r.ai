-- ==========================================
-- ROLLBACK для МИГРАЦИИ v0.4.1 - ГЕНЕРАЦИЯ РЕЦЕПТОВ
-- ==========================================
-- Date: 2025-01-19
-- Purpose: Rollback recipe generation functionality
-- Rollback for: 2025-01-19_recipe_migration.sql

-- Удалить view для активности пользователей
DROP VIEW IF EXISTS user_activity_summary;

-- Удалить индексы
DROP INDEX IF EXISTS idx_logs_user_action_timestamp;
DROP INDEX IF EXISTS idx_logs_action_type;
DROP INDEX IF EXISTS idx_user_profiles_telegram_id;
DROP INDEX IF EXISTS idx_user_profiles_updated_at;

-- Удалить таблицу user_profiles
DROP TABLE IF EXISTS user_profiles;

-- Удалить новые типы действий из logs (осторожно - может повлиять на существующие данные)
-- Примечание: Этот rollback может привести к потере данных, если уже есть записи с новыми типами действий
-- DELETE FROM logs WHERE action_type IN ('recipe_generation', 'profile_update', 'calorie_calculation');

-- Удалить новые столбцы из таблицы users
ALTER TABLE users DROP COLUMN IF EXISTS subscription_type;
ALTER TABLE users DROP COLUMN IF EXISTS subscription_expires_at;

-- Восстановить исходное состояние таблицы users (если необходимо)
-- Примечание: Этот rollback предполагает, что исходная структура была без этих полей

-- Удалить функции для расчета калорий (если они были созданы)
DROP FUNCTION IF EXISTS calculate_bmr(INTEGER, REAL, REAL, TEXT);
DROP FUNCTION IF EXISTS calculate_daily_calories(INTEGER, REAL, REAL, TEXT, TEXT);

-- Примечание: Этот rollback может привести к потере данных пользователей
-- Рекомендуется создать резервную копию перед выполнением rollback