# Database Migrations

This directory contains all database migration files organized by type and date.

## Structure

```
migrations/
├── README.md                    # This file
├── database/                    # Database schema migrations
│   ├── 2025-07-20_recipe_migration.sql
│   ├── 2025-07-20_constraints.sql
│   └── 2025-07-20_multilingual.sql
├── rollbacks/                   # Rollback scripts
│   ├── 2025-07-20_recipe_migration_rollback.sql
│   └── 2025-07-20_constraints_rollback.sql
└── schema/                      # Schema definitions
    └── schema.sql
```

## Migration Naming Convention

All migration files follow the naming pattern:
`YYYY-MM-DD_description.sql`

## Migration Types

### Database Migrations (`database/`)
- Schema changes (CREATE TABLE, ALTER TABLE, etc.)
- Data migrations
- Index creation/modification
- Constraint additions

### Rollback Scripts (`rollbacks/`)
- Corresponding rollback for each migration
- Named with `_rollback` suffix
- Should undo changes made by the main migration

### Schema Definitions (`schema/`)
- Complete database schema definitions
- Reference schemas for different environments

## Usage

### Running Migrations
```bash
# Connect to your database
psql -h your-host -d your-database -U your-user

# Run a specific migration
\i migrations/database/2025-07-20_recipe_migration.sql

# Or run via command line
psql -h your-host -d your-database -U your-user -f migrations/database/2025-07-20_recipe_migration.sql
```

### Rolling Back
```bash
# Run the corresponding rollback script
\i migrations/rollbacks/2025-07-20_recipe_migration_rollback.sql
```

## Migration History

| Date | Migration | Description | Status |
|------|-----------|-------------|--------|
| 2025-07-20 | recipe_migration | Added recipe generation functionality | ✅ Applied |
| 2025-07-20 | constraints | Added database constraints | ✅ Applied |
| 2025-07-20 | multilingual | Added multilingual support | ✅ Applied |

## Best Practices

1. **Always create rollback scripts** for each migration
2. **Test migrations** in development environment first
3. **Backup database** before running migrations in production
4. **Document changes** in this README when adding new migrations
5. **Use descriptive names** for migration files
6. **Include comments** in SQL files explaining the changes

## Migration Checklist

Before applying a migration:
- [ ] Migration tested in development
- [ ] Rollback script created and tested
- [ ] Database backup created
- [ ] Migration documented in history table above
- [ ] Team notified of schema changes