# Database Migrations Guide

## Overview
Automated database migration system for c0r.ai API project. Supports development and production environments with automatic deployment through GitHub Actions.

## Quick Start

### Creating a Migration
1. Create migration file: `migrations/database/YYYY-MM-DD_description.sql`
2. Create rollback file: `migrations/rollbacks/YYYY-MM-DD_description_rollback.sql`
3. Test locally: `env ENVIRONMENT=development DB_PASSWORD='&vh1NzI6wwiUx' ./scripts/run_migrations.sh`
4. Commit and push: migrations automatically apply to production via GitHub Actions

### Commands
- **Development**: `env ENVIRONMENT=development DB_PASSWORD='&vh1NzI6wwiUx' ./scripts/run_migrations.sh`
- **Production (manual)**: `env ENVIRONMENT=production DB_PASSWORD='xuoO4|LSaaGX5' ./scripts/run_migrations.sh`
- **Production (auto)**: Push to main branch triggers GitHub Actions

## Migration Template

### Standard Migration (`migrations/database/`)
```sql
-- Migration: Description of what this migration does
-- Created: YYYY-MM-DD
-- Added by: [Your name]
-- Purpose: [Purpose description]

-- Check if this migration was already applied
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.migrations_log WHERE migration_name = 'YYYY-MM-DD_your_migration_name.sql') THEN

        -- Your migration code here
        CREATE TABLE IF NOT EXISTS public.your_table (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            -- Add your columns
        );

        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_your_table_field ON public.your_table(field);

        -- Grant permissions
        GRANT ALL ON public.your_table TO postgres;
        GRANT ALL ON public.your_table TO service_role;
        GRANT SELECT, INSERT, UPDATE ON public.your_table TO anon;
        GRANT SELECT, INSERT, UPDATE ON public.your_table TO authenticated;

        -- Log this migration
        INSERT INTO public.migrations_log (migration_name)
        VALUES ('YYYY-MM-DD_your_migration_name.sql');

        RAISE NOTICE 'Migration YYYY-MM-DD_your_migration_name.sql applied successfully';
    ELSE
        RAISE NOTICE 'Migration YYYY-MM-DD_your_migration_name.sql already applied, skipping';
    END IF;
END $$;
```

### Rollback Template (`migrations/rollbacks/`)
```sql
-- Rollback: Description of rollback
-- Created: YYYY-MM-DD
-- Purpose: Rollback for YYYY-MM-DD_your_migration_name.sql

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'your_table') THEN
        DROP TABLE IF EXISTS public.your_table CASCADE;
        DELETE FROM public.migrations_log WHERE migration_name = 'YYYY-MM-DD_your_migration_name.sql';
        INSERT INTO public.migrations_log (migration_name, applied_at)
        VALUES ('YYYY-MM-DD_your_migration_name_rollback.sql', CURRENT_TIMESTAMP);
        RAISE NOTICE 'Rollback completed: your_table dropped';
    ELSE
        RAISE NOTICE 'your_table does not exist, nothing to rollback';
    END IF;
END $$;
```

## Database Configuration

### Development Database
- **Host**: `aws-0-eu-north-1.pooler.supabase.com`
- **User**: `postgres.cadeererdjwemspkeriq`
- **Password**: `&vh1NzI6wwiUx`
- **Port**: `6543`
- **Database**: `postgres`

### Production Database
- **Host**: `aws-0-eu-central-1.pooler.supabase.com`
- **User**: `postgres.mmrzpngugivxoapjiovb`
- **Password**: `xuoO4|LSaaGX5`
- **Port**: `6543`
- **Database**: `postgres`

## Rules and Best Practices

### ✅ DO
- Always create both migration and rollback files
- Test migrations locally in development before pushing
- Use idempotent migrations (check if already applied)
- Include descriptive comments and RAISE NOTICE messages
- Follow naming convention: `YYYY-MM-DD_description.sql`
- Use `IF NOT EXISTS` for table/index creation
- Grant proper permissions after creating tables
- Log all migrations in `migrations_log` table

### ❌ DON'T
- Never run migrations directly on production without testing
- Don't modify existing migration files after they're applied
- Don't forget to create rollback files
- Don't hardcode sensitive data in migration files
- Don't break existing functionality with schema changes

### Migration Order
1. Create migration files locally
2. Test in development: `env ENVIRONMENT=development DB_PASSWORD='&vh1NzI6wwiUx' ./scripts/run_migrations.sh`
3. Verify table/changes exist in development database
4. Commit both migration and rollback files
5. Push to main branch
6. GitHub Actions automatically applies to production
7. Verify changes in production database

## Troubleshooting

### Common Issues
- **Migration already applied**: Check `migrations_log` table for existing entries
- **Permission denied**: Verify database credentials and permissions
- **Connection failed**: Check database host, port, and network connectivity
- **GitHub Actions fails**: Check workflow logs and ensure `DB_PASSWORD` secret is set

### Debugging Commands
```bash
# Check migration status
SELECT migration_name, applied_at FROM public.migrations_log ORDER BY applied_at DESC;

# List all tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

# Test migration script with verbose output
env ENVIRONMENT=development DB_PASSWORD='&vh1NzI6wwiUx' ./scripts/run_migrations.sh | tail -20
```

## Files Structure
```
migrations/
├── database/           # Migration files
├── rollbacks/          # Rollback files
scripts/
├── run_migrations.sh   # Main migration runner
.github/workflows/
├── deploy.yml          # GitHub Actions with auto-migrations
```

## GitHub Actions Integration
Migrations automatically run during deployment when:
- Code is pushed to `main` branch
- `scripts/run_migrations.sh` exists
- `DB_PASSWORD` secret is configured in GitHub

The workflow executes:
```bash
env CI=true ENVIRONMENT=production DB_PASSWORD='${{ secrets.DB_PASSWORD }}' ./scripts/run_migrations.sh
```