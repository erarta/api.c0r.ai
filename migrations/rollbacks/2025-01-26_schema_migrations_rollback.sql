-- Rollback: Drop schema_migrations table
-- Date: 2025-01-26
-- Description: Rollback migration system setup

-- Drop indexes first
DROP INDEX IF EXISTS idx_schema_migrations_applied_at;
DROP INDEX IF EXISTS idx_schema_migrations_filename;

-- Drop the schema_migrations table
DROP TABLE IF EXISTS schema_migrations;