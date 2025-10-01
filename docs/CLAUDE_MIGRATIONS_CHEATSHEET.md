# Claude Code - Migrations Cheatsheet

> Quick reference for Claude Code when creating database migrations

## ⚡ Quick Commands

### Test Migration Locally
```bash
env ENVIRONMENT=development DB_PASSWORD='&vh1NzI6wwiUx' ./scripts/run_migrations.sh
```

### Deploy to Production (automatic via GitHub Actions)
```bash
git add migrations/database/file.sql migrations/rollbacks/file_rollback.sql
git commit -m "feat: Add [description] migration"
git push origin main
```

## 📁 File Naming Convention
- **Migration**: `migrations/database/YYYY-MM-DD_description.sql`
- **Rollback**: `migrations/rollbacks/YYYY-MM-DD_description_rollback.sql`

## 🔧 Migration Template (Copy-Paste Ready)

### migrations/database/YYYY-MM-DD_description.sql
```sql
-- Migration: [Brief description]
-- Created: 2025-MM-DD
-- Added by: Claude for [purpose]

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM public.migrations_log WHERE migration_name = 'YYYY-MM-DD_description.sql') THEN

        CREATE TABLE IF NOT EXISTS public.table_name (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            -- Add columns here
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_table_name_field ON public.table_name(field);

        GRANT ALL ON public.table_name TO postgres;
        GRANT ALL ON public.table_name TO service_role;
        GRANT SELECT, INSERT, UPDATE ON public.table_name TO anon;
        GRANT SELECT, INSERT, UPDATE ON public.table_name TO authenticated;

        INSERT INTO public.migrations_log (migration_name)
        VALUES ('YYYY-MM-DD_description.sql');

        RAISE NOTICE 'Migration YYYY-MM-DD_description.sql applied successfully';
    ELSE
        RAISE NOTICE 'Migration YYYY-MM-DD_description.sql already applied, skipping';
    END IF;
END $$;
```

### migrations/rollbacks/YYYY-MM-DD_description_rollback.sql
```sql
-- Rollback: Remove [description]
-- Created: 2025-MM-DD

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'table_name') THEN
        DROP TABLE IF EXISTS public.table_name CASCADE;
        DELETE FROM public.migrations_log WHERE migration_name = 'YYYY-MM-DD_description.sql';
        INSERT INTO public.migrations_log (migration_name, applied_at)
        VALUES ('YYYY-MM-DD_description_rollback.sql', CURRENT_TIMESTAMP);
        RAISE NOTICE 'Rollback completed: table_name dropped';
    ELSE
        RAISE NOTICE 'table_name does not exist, nothing to rollback';
    END IF;
END $$;
```

## 🗄️ Database Info

| Environment | Host | User | Password | Port |
|------------|------|------|----------|------|
| **Development** | aws-0-eu-north-1.pooler.supabase.com | postgres.cadeererdjwemspkeriq | `&vh1NzI6wwiUx` | 6543 |
| **Production** | aws-0-eu-central-1.pooler.supabase.com | postgres.mmrzpngugivxoapjiovb | `xuoO4|LSaaGX5` | 6543 |

## ✅ Workflow Checklist

1. **Create migration files** (both migration + rollback)
2. **Test locally**: `env ENVIRONMENT=development DB_PASSWORD='&vh1NzI6wwiUx' ./scripts/run_migrations.sh`
3. **Verify in dev DB**: Check table exists and has expected structure
4. **Commit files**: `git add migrations/...`
5. **Push to main**: GitHub Actions automatically deploys to production
6. **Verify in prod**: Table should appear in production database

## 🚨 Important Notes

- **ALWAYS** create both migration and rollback files
- **ALWAYS** test in development first
- **NEVER** modify existing migration files after they're applied
- **NEVER** commit sensitive data in migration files
- Use `IF NOT EXISTS` for idempotent operations
- Include descriptive RAISE NOTICE messages
- Follow the exact template structure for consistency

## 🔍 Debugging Commands

```bash
# Check migration logs
PGPASSWORD='password' psql -h host -U user -d postgres -p 6543 -c "SELECT migration_name, applied_at FROM public.migrations_log ORDER BY applied_at DESC LIMIT 10;"

# List tables
PGPASSWORD='password' psql -h host -U user -d postgres -p 6543 -c "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
```