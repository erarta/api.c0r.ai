# Database Schema Files

This directory contains database schema definitions and structure files.

## Directory Structure

```
migrations/schema/
├── README.md                    # This file
├── initial_schema.sql          # Initial database schema
├── tables/                     # Table definitions
│   ├── users.sql              # Users table schema
│   ├── logs.sql               # Logs table schema
│   ├── payments.sql           # Payments table schema
│   └── user_profiles.sql      # User profiles table schema
├── views/                     # Database views
│   └── user_activity_summary.sql
├── functions/                 # Database functions
│   └── calorie_calculations.sql
└── indexes/                   # Index definitions
    ├── users_indexes.sql
    ├── logs_indexes.sql
    └── payments_indexes.sql
```

## Usage Guidelines

### Schema Files
- **initial_schema.sql**: Complete initial database schema for new installations
- **tables/**: Individual table definitions for reference and maintenance
- **views/**: Database view definitions
- **functions/**: Custom database functions
- **indexes/**: Index definitions organized by table

### Best Practices
1. Keep schema files synchronized with migrations
2. Update schema files when creating new migrations
3. Use descriptive comments in schema files
4. Include constraints and indexes in table definitions
5. Document relationships between tables

### Schema Versioning
- Schema files represent the current state after all migrations
- Use migration files for incremental changes
- Schema files serve as reference and for fresh installations

## Related Files
- See `../database/` for migration files
- See `../rollbacks/` for rollback scripts
- See `../README.md` for overall migration system documentation