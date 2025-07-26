-- Migration: Create schema_migrations table for tracking applied migrations
-- Date: 2025-01-26
-- Description: Add system for tracking database migrations

-- Create schema_migrations table if it doesn't exist
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) UNIQUE NOT NULL,
    applied_at TIMESTAMP DEFAULT NOW(),
    rollback_filename VARCHAR(255),
    checksum VARCHAR(64),
    status VARCHAR(20) DEFAULT 'applied',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Add comment to table
COMMENT ON TABLE schema_migrations IS 'Tracks applied database migrations';
COMMENT ON COLUMN schema_migrations.filename IS 'Name of the migration file';
COMMENT ON COLUMN schema_migrations.applied_at IS 'When the migration was applied';
COMMENT ON COLUMN schema_migrations.rollback_filename IS 'Name of the corresponding rollback file';
COMMENT ON COLUMN schema_migrations.checksum IS 'SHA256 checksum of the migration file';
COMMENT ON COLUMN schema_migrations.status IS 'Status: applied, rolled_back, failed';

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_schema_migrations_filename ON schema_migrations(filename);
CREATE INDEX IF NOT EXISTS idx_schema_migrations_applied_at ON schema_migrations(applied_at);

-- Insert this migration record
INSERT INTO schema_migrations (filename, rollback_filename, checksum, status) 
VALUES (
    '2025-01-26_schema_migrations.sql',
    '2025-01-26_schema_migrations_rollback.sql',
    'initial_migration_system',
    'applied'
) ON CONFLICT (filename) DO NOTHING;