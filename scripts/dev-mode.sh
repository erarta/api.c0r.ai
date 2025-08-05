#!/bin/bash

# Development Mode Script for C0R.AI
# Enables hot-reload for fast development without Docker cache rebuilds

set -e

echo "🚀 Starting C0R.AI in Development Mode with Hot-Reload..."

# Function to display colored output
print_status() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

# Check if docker-compose.override.yml exists
if [ ! -f "docker-compose.override.yml" ]; then
    print_error "docker-compose.override.yml not found! Hot-reload will not work."
    exit 1
fi

print_status "Using hot-reload configuration from docker-compose.override.yml"

# Stop any running containers
print_status "Stopping existing containers..."
docker-compose down

# Start in development mode
print_status "Starting containers with hot-reload..."
docker-compose up -d

# Wait for services to start
print_status "Waiting for services to start..."
sleep 10

# Check service health
print_status "Checking service health..."

check_service() {
    local service=$1
    local port=$2
    local name=$3
    
    if curl -sf http://localhost:$port/health > /dev/null 2>&1; then
        print_success "$name service is healthy"
        return 0
    else
        print_error "$name service is unhealthy"
        return 1
    fi
}

all_healthy=true

check_service "ml" "8001" "ML" || all_healthy=false
check_service "api" "8000" "API" || all_healthy=false
check_service "pay" "8002" "Payment" || all_healthy=false

if $all_healthy; then
    print_success "🎉 All services are running and healthy!"
    print_success "Hot-reload is active - changes to Python files will auto-reload"
    echo ""
    echo "📊 Service URLs:"
    echo "  • API: http://localhost:8000"
    echo "  • ML:  http://localhost:8001" 
    echo "  • Pay: http://localhost:8002"
    echo ""
    echo "📝 Development Tips:"
    echo "  • Edit files in services/ directories"
    echo "  • Changes auto-reload without rebuilds"
    echo "  • Use 'docker-compose logs <service>' to view logs"
    echo "  • Use 'docker-compose ps' to check status"
    echo ""
    print_warning "Remember: This is development mode. Use 'docker-compose build' for production."
else
    print_error "Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi 