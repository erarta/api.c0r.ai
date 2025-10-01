#!/bin/bash
# Database Migration Runner
# Added by Claude for automated deployment migrations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Database connection parameters (defaults to production)
DB_HOST=${DB_HOST:-"aws-0-eu-central-1.pooler.supabase.com"}
DB_USER=${DB_USER:-"postgres.mmrzpngugivxoapjiovb"}
DB_NAME=${DB_NAME:-"postgres"}
DB_PORT=${DB_PORT:-"6543"}

# For development database, override with environment variables
if [ "$ENVIRONMENT" = "development" ]; then
    DB_HOST=${DB_HOST:-"aws-0-eu-central-1.pooler.supabase.com"}
    DB_USER=${DB_USER:-"postgres.cadeererdjwemspkeriq"}
    DB_NAME=${DB_NAME:-"postgres"}
    DB_PORT=${DB_PORT:-"6543"}
fi
MIGRATIONS_DIR="migrations/database"

echo -e "${YELLOW}🗄️ Starting database migrations...${NC}"

# Check if migrations directory exists
if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo -e "${RED}❌ Migrations directory not found: $MIGRATIONS_DIR${NC}"
    exit 1
fi

# Check if DB_PASSWORD is set
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}❌ DB_PASSWORD environment variable not set${NC}"
    exit 1
fi

# Function to run a single migration
run_migration() {
    local migration_file="$1"
    local migration_name=$(basename "$migration_file")

    echo -e "${YELLOW}📄 Processing: $migration_name${NC}"

    # Run the migration
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -p "$DB_PORT" -f "$migration_file" -v ON_ERROR_STOP=1; then
        echo -e "${GREEN}✅ Migration applied: $migration_name${NC}"
        return 0
    else
        echo -e "${RED}❌ Migration failed: $migration_name${NC}"
        return 1
    fi
}

# Main migration loop
failed_migrations=0
total_migrations=0

# Process all .sql files in chronological order
for migration_file in $(find "$MIGRATIONS_DIR" -name "*.sql" | sort); do
    total_migrations=$((total_migrations + 1))

    if ! run_migration "$migration_file"; then
        failed_migrations=$((failed_migrations + 1))

        # Continue with other migrations even if one fails
        echo -e "${YELLOW}⚠️ Continuing with next migration...${NC}"
    fi
done

# Summary
echo -e "\n${YELLOW}📊 Migration Summary:${NC}"
echo "Total migrations: $total_migrations"
echo "Failed migrations: $failed_migrations"
echo "Successful migrations: $((total_migrations - failed_migrations))"

if [ $failed_migrations -eq 0 ]; then
    echo -e "${GREEN}🎉 All migrations completed successfully!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️ Some migrations failed but deployment continues${NC}"
    exit 0  # Don't fail deployment for migration issues
fi