#!/bin/bash
# c0r.ai Production Deployment Script
# This script deploys the application to production with comprehensive testing

set -e  # Exit on any error

echo "🚀 Starting c0r.ai Production Deployment"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

print_status "Project root: $PROJECT_ROOT"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Make sure you're in the project root."
    exit 1
fi

# Step 1: Pull latest changes
print_status "Pulling latest changes from git..."
git pull origin main

# Step 2: Run comprehensive tests before deployment
print_status "Running comprehensive tests before deployment..."
echo "🧪 MANDATORY: All tests must pass before deployment"

# Run deployment tests
if ! ./tests/deploy_test.sh; then
    print_error "DEPLOYMENT BLOCKED: Tests failed"
    print_error "Fix the failing tests and try again"
    exit 1
fi

print_status "✅ All tests passed! Proceeding with deployment..."

# Step 2.5: Load environment and create DB backup before migrations
print_status "Loading environment from .env..."
if [ -f .env ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
else
    print_error ".env not found. DATABASE_URL must be set."
    exit 1
fi

: "${DATABASE_URL:?DATABASE_URL must be set in .env (URL-encoded password and sslmode=require)}"

print_status "Creating database backup before migrations..."
# Use local backup script; requires postgresql-client on host
BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"
if BACKUP_DIR="$BACKUP_DIR" PG_URI="$DATABASE_URL" bash ./scripts/pg_backup.sh; then
    print_status "✅ Database backup completed"
else
    print_error "❌ Database backup failed. Aborting deployment."
    exit 1
fi

# Step 2.6: Run DB migrations; abort on failure
print_status "Running database migrations..."
if docker-compose run --rm api python scripts/run_migrations.py --database-url "$DATABASE_URL"; then
    print_status "✅ Migrations applied successfully"
else
    print_error "❌ Migrations failed. Aborting deployment."
    exit 1
fi

# Step 3: Stop existing containers
print_status "Stopping existing containers..."
docker-compose down

# Step 4: Remove old images to free space
print_status "Cleaning up old Docker images..."
docker system prune -f

# Step 5: Build new images
print_status "Building new Docker images..."
docker-compose build --no-cache

# Step 6: Start services
print_status "Starting services..."
docker-compose up -d

# Step 7: Wait for services to start
print_status "Waiting for services to start..."
sleep 30

# Step 8: Check service status
print_status "Checking service status..."
docker-compose ps

# Step 9: Display recent logs
print_status "Checking recent logs..."
docker-compose logs --tail=20

# Step 10: Health checks
print_status "Running health checks..."

# Check if services are running
if ! docker-compose ps | grep -q "Up"; then
    print_error "Some services failed to start"
    docker-compose logs
    exit 1
fi

print_status "✅ Deployment completed successfully!"
print_status "Services are running and healthy"

# Step 11: Display helpful information
echo ""
echo "📊 Deployment Summary:"
echo "====================="
echo "• Tests passed: ✅"
echo "• Docker containers: ✅"
echo "• Services health: ✅"
echo ""
echo "🔗 Next steps:"
echo "• Check service logs: docker-compose logs -f"
echo "• Monitor service health: docker-compose ps"
echo "• Test endpoints manually"
echo ""
echo "🎉 Deployment completed successfully!" 