# Database Migrations

This directory contains all database migration files organized by type and date with automated tracking system.

## 🏗️ Structure

```
migrations/
├── README.md                    # This file
├── database/                    # Database schema migrations
│   ├── 2025-01-26_schema_migrations.sql
│   ├── 2025-01-21_constraints.sql
│   └── 2025-01-21_multilingual.sql
├── rollbacks/                   # Rollback scripts
│   ├── 2025-01-26_schema_migrations_rollback.sql
│   ├── 2025-01-21_constraints_rollback.sql
│   └── 2025-01-21_multilingual_rollback.sql
└── schema/                      # Schema definitions
    └── initial_schema.sql
```

## 🚀 Automated Migration System (Updated by Claude)

### Migration Tracking
- All migrations are tracked in `migrations_log` table
- Automatic duplicate prevention with idempotent migrations
- **Auto-deployment integration** - migrations run on every deploy
- Built-in rollback support with tracking

### Running Migrations
```bash
# Automated migration runner (recommended - used in GitHub Actions)
./scripts/run_migrations.sh

# Legacy Python runner (deprecated)
python scripts/run_migrations.py

# Manual migration (for specific cases only)
psql -h aws-0-eu-central-1.pooler.supabase.com -U postgres.mmrzpngugivxoapjiovb -d postgres -p 6543 -f migrations/database/migration_file.sql
```

### GitHub Actions Integration
- Migrations run automatically on every push to `main`
- No more manual migration applying on production!
- Failures don't block deployment (warnings only)
- Full logging in GitHub Actions workflow

### Rolling Back
```bash
# Automated rollback (coming soon)
python scripts/rollback_migration.py migration_name

# Manual rollback
psql -h your-host -d your-database -U your-user -f migrations/rollbacks/migration_rollback.sql
```

## 📋 Migration Naming Convention

All migration files follow the pattern: `YYYY-MM-DD_description.sql`

**Examples:**
- `2025-01-26_schema_migrations.sql` - Migration tracking system
- `2025-01-21_multilingual.sql` - Multilingual support
- `2025-01-21_constraints.sql` - Database constraints

## 📊 Migration Types

### Database Migrations (`database/`)
- Schema changes (CREATE TABLE, ALTER TABLE, etc.)
- Data migrations and transformations
- Index creation/modification
- Constraint additions
- System table creation

### Rollback Scripts (`rollbacks/`)
- Corresponding rollback for each migration
- Named with `_rollback` suffix
- Should completely undo changes made by main migration
- Tracked in `schema_migrations` table

### Schema Definitions (`schema/`)
- Complete database schema definitions
- Reference schemas for different environments
- Initial setup scripts

## 📈 Migration History

| Date | Migration | Description | Status |
|------|-----------|-------------|--------|
| 2025-09-25 | enhanced_nutrition_system | Enhanced AI nutrition features with DNA profiling | 🚀 Ready |
| 2025-08-10 | user_profiles_avatar_fullname | User profile enhancements | ✅ Applied |
| 2025-08-08 | features_favorites_plans_recipes | Core features and favorites | ✅ Applied |
| 2025-01-26 | schema_migrations | Migration tracking system | ✅ Applied |

## ✅ Best Practices

1. **Use automated runner** - `python scripts/run_migrations.py`
2. **Always create rollback scripts** for each migration
3. **Test migrations** in development environment first
4. **Include descriptive comments** in SQL files
5. **Follow naming convention** strictly
6. **Update this README** when adding new migrations
7. **Use migration tracking** - never run migrations manually in production

## 🔧 Migration Checklist

Before creating a migration:
- [ ] Migration follows naming convention
- [ ] Rollback script created and tested
- [ ] Migration tested in development
- [ ] Comments added explaining changes
- [ ] README updated with migration info
- [ ] Migration added to tracking system

Before applying in production:
- [ ] Database backup created
- [ ] Migration runner script used
- [ ] Service bot notifications configured
- [ ] Team notified of schema changes

## 🚨 Emergency Procedures

### Failed Migration Recovery
1. Check `schema_migrations` table for status
2. Run corresponding rollback script
3. Fix migration issues
4. Re-run migration with fixes

### Manual Migration Tracking
If you need to manually mark a migration as applied:
```sql
INSERT INTO schema_migrations (filename, rollback_filename, checksum, status)
VALUES ('migration_name.sql', 'migration_name_rollback.sql', 'manual_checksum', 'applied');
```