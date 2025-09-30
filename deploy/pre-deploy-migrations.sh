#!/bin/bash
# Pre-deployment Migration Script for c0r.ai Enhanced Nutrition System
# Runs database migrations before application deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DATABASE_URL="${DATABASE_URL:-postgresql://postgres.cadeererdjwemspkeriq:xuoO4|LSaaGX5@aws-0-eu-north-1.pooler.supabase.com:6543/postgres}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    error "DATABASE_URL environment variable is not set"
    exit 1
fi

log "🚀 Starting pre-deployment migration process..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed"
    exit 1
fi

# Check if required packages are installed
log "📦 Checking Python dependencies..."
python3 -c "import psycopg2, loguru" 2>/dev/null || {
    error "Required Python packages not found. Installing..."
    pip3 install psycopg2-binary loguru
}

# Verify database connection
log "🔌 Testing database connection..."
python3 -c "
import psycopg2
import sys

try:
    conn = psycopg2.connect('$DATABASE_URL')
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
" || exit 1

# Run dry-run first to check what migrations would be applied
log "🧪 Running migration dry-run..."
cd "$PROJECT_ROOT"
python3 scripts/run_migrations.py --database-url "$DATABASE_URL" --dry-run

# Ask for confirmation in interactive mode
if [ -t 0 ]; then  # Check if running in terminal (interactive)
    echo ""
    read -p "Continue with migrations? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warning "Migration cancelled by user"
        exit 0
    fi
fi

# Create database backup (optional - depends on your backup strategy)
log "💾 Creating database backup timestamp..."
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
echo "Backup timestamp: $BACKUP_TIMESTAMP (for rollback reference)"

# Run actual migrations
log "⚡ Running database migrations..."
if python3 scripts/run_migrations.py --database-url "$DATABASE_URL"; then
    log "✅ All migrations completed successfully!"
else
    error "❌ Migration failed! Check logs above for details."
    error "🔄 You may need to run rollback if database is in inconsistent state"
    exit 1
fi

# Verify critical tables exist
log "🔍 Verifying enhanced nutrition tables..."
python3 -c "
import psycopg2

tables_to_check = [
    'nutrition_questionnaire_responses',
    'nutrition_dna',
    'meal_recommendations',
    'user_food_analysis_enhanced'
]

try:
    conn = psycopg2.connect('$DATABASE_URL')
    cur = conn.cursor()

    for table in tables_to_check:
        cur.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)\", (table,))
        exists = cur.fetchone()[0]
        if exists:
            print(f'✅ Table {table} exists')
        else:
            print(f'❌ Table {table} missing')
            raise Exception(f'Required table {table} not found')

    conn.close()
    print('✅ All required tables verified')
except Exception as e:
    print(f'❌ Table verification failed: {e}')
    exit(1)
" || exit 1

# Check enhanced user_profiles columns
log "🔍 Verifying user_profiles enhancements..."
python3 -c "
import psycopg2

required_columns = [
    'onboarding_completed',
    'favorite_foods',
    'preferred_cuisines',
    'cooking_skill',
    'social_eating_frequency'
]

try:
    conn = psycopg2.connect('$DATABASE_URL')
    cur = conn.cursor()

    cur.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name = 'user_profiles'\")
    existing_columns = [row[0] for row in cur.fetchall()]

    for column in required_columns:
        if column in existing_columns:
            print(f'✅ Column {column} exists in user_profiles')
        else:
            print(f'❌ Column {column} missing from user_profiles')
            raise Exception(f'Required column {column} not found')

    conn.close()
    print('✅ user_profiles enhancements verified')
except Exception as e:
    print(f'❌ user_profiles verification failed: {e}')
    exit(1)
" || exit 1

# Test API endpoints (if application is already running)
log "🌐 Testing enhanced nutrition API endpoints..."
if command -v curl &> /dev/null && [ ! -z "$API_URL" ]; then
    # Test basic endpoint availability
    if curl -sf "$API_URL/health" > /dev/null 2>&1; then
        log "✅ API is responding"

        # Test specific enhanced nutrition endpoints
        endpoints_to_test=(
            "/nutrition-onboarding/questionnaire-summary"
            "/health/nutrition-system"
        )

        for endpoint in "${endpoints_to_test[@]}"; do
            if curl -sf "$API_URL$endpoint" > /dev/null 2>&1; then
                log "✅ Endpoint $endpoint responding"
            else
                warning "⚠️  Endpoint $endpoint not responding (may be normal if auth required)"
            fi
        done
    else
        warning "⚠️  API not responding (may be normal during deployment)"
    fi
else
    warning "⚠️  Skipping API tests (curl not available or API_URL not set)"
fi

# Final success message
log "🎉 Pre-deployment migrations completed successfully!"
log "📊 Enhanced Nutrition System database schema is ready"
log "🚀 Proceed with application deployment"

# Output summary for CI/CD logs
echo ""
echo "=================================="
echo "MIGRATION SUMMARY"
echo "=================================="
echo "Status: SUCCESS ✅"
echo "Timestamp: $(date)"
echo "Database: $(echo $DATABASE_URL | sed 's/:[^@]*@/:***@/')"  # Hide password in logs
echo "Enhanced tables: nutrition_dna, meal_recommendations, questionnaire_responses, enhanced_analysis"
echo "Extended tables: user_profiles (20+ new columns), meal_plans (dna integration)"
echo "Ready for: Enhanced AI nutrition features"
echo "=================================="