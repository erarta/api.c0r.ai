#!/bin/bash

# Local Docker Testing Script for c0r.ai
# Tests all Docker containers and services locally

set -e  # Exit on any error

echo "🐳 Starting Local Docker Testing for c0r.ai"
echo "=============================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo
print_info "Checking prerequisites..."

if ! command_exists docker; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command_exists docker-compose; then
    if ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not available. Please install docker-compose or use Docker with compose plugin."
        exit 1
    fi
    DOCKER_COMPOSE_CMD="docker compose"
else
    DOCKER_COMPOSE_CMD="docker-compose"
fi

print_status "Docker is available"
print_status "Docker Compose is available"

# Check if Docker daemon is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker daemon is not running. Please start Docker first."
    exit 1
fi

print_status "Docker daemon is running"

# Function to wait for service to be ready
wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    print_info "Waiting for $service_name to be ready on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f http://localhost:$port/ >/dev/null 2>&1; then
            print_status "$service_name is ready!"
            return 0
        fi
        
        if [ $((attempt % 5)) -eq 0 ]; then
            print_info "Still waiting for $service_name... (attempt $attempt/$max_attempts)"
        fi
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within expected time"
    return 1
}

# Function to test service endpoint
test_service() {
    local service_name=$1
    local port=$2
    local endpoint=$3
    
    print_info "Testing $service_name endpoint..."
    
    if curl -s -f http://localhost:$port$endpoint >/dev/null 2>&1; then
        print_status "$service_name endpoint is working"
        return 0
    else
        print_error "$service_name endpoint test failed"
        return 1
    fi
}

# Function to check service logs
check_service_logs() {
    local service_name=$1
    
    print_info "Checking $service_name logs for errors..."
    
    # Get last 10 lines of logs
    logs=$($DOCKER_COMPOSE_CMD logs --tail=10 $service_name 2>/dev/null || echo "")
    
    if echo "$logs" | grep -i error >/dev/null 2>&1; then
        print_warning "$service_name has errors in logs"
        echo "$logs" | grep -i error
    else
        print_status "$service_name logs look clean"
    fi
}

# Function to check .env file
check_env_file() {
    if [ ! -f ".env" ]; then
        print_error ".env file not found! Creating from example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "Created .env from .env.example. Please configure it with your actual values."
        else
            print_error "No .env.example found either. Please create .env file manually."
            return 1
        fi
    else
        print_status ".env file exists"
    fi
}

# Main testing flow
echo
print_info "Starting Docker testing process..."

# Step 1: Check .env file
check_env_file

# Step 2: Stop any existing containers
print_info "Stopping any existing containers..."
$DOCKER_COMPOSE_CMD down >/dev/null 2>&1 || true

# Step 3: Clean up old images (optional)
read -p "Do you want to clean up old Docker images? (y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Cleaning up old Docker images..."
    docker system prune -f >/dev/null 2>&1 || true
    print_status "Cleanup completed"
fi

# Step 4: Build containers
echo
print_info "Building Docker containers..."
if $DOCKER_COMPOSE_CMD build --no-cache; then
    print_status "Containers built successfully"
else
    print_error "Container build failed"
    exit 1
fi

# Step 5: Start containers
echo
print_info "Starting Docker containers..."
if $DOCKER_COMPOSE_CMD up -d; then
    print_status "Containers started successfully"
else
    print_error "Failed to start containers"
    exit 1
fi

# Step 6: Wait for services to be ready
echo
print_info "Waiting for services to be ready..."

# Wait for each service (adjust ports based on your docker-compose.yml)
services_failed=0

# API service (assuming port 8000)
if wait_for_service "API" "8000"; then
    test_service "API" "8000" "/" || services_failed=$((services_failed + 1))
    check_service_logs "api"
else
    services_failed=$((services_failed + 1))
fi

# ML service (assuming port 8001)
if wait_for_service "ML" "8001"; then
    test_service "ML" "8001" "/" || services_failed=$((services_failed + 1))
    check_service_logs "ml"
else
    services_failed=$((services_failed + 1))
fi

# Pay service (assuming port 8002)
if wait_for_service "Pay" "8002"; then
    test_service "Pay" "8002" "/" || services_failed=$((services_failed + 1))
    check_service_logs "pay"
else
    services_failed=$((services_failed + 1))
fi

# Step 7: Show container status
echo
print_info "Container status:"
$DOCKER_COMPOSE_CMD ps

# Step 8: Show resource usage
echo
print_info "Resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Step 9: Run basic health checks
echo
print_info "Running additional health checks..."

# Check if containers are still running
running_containers=$($DOCKER_COMPOSE_CMD ps -q | wc -l)
if [ "$running_containers" -gt 0 ]; then
    print_status "All containers are running"
else
    print_error "Some containers may have stopped"
    services_failed=$((services_failed + 1))
fi

# Step 10: Final results
echo
echo "=============================================="
if [ $services_failed -eq 0 ]; then
    print_status "🎉 All Docker services are working correctly!"
    echo
    print_info "Next steps:"
    echo "  • Services are running at:"
    echo "    - API: http://localhost:8000"
    echo "    - ML:  http://localhost:8001" 
    echo "    - Pay: http://localhost:8002"
    echo "  • View logs: $DOCKER_COMPOSE_CMD logs -f"
    echo "  • Stop services: $DOCKER_COMPOSE_CMD down"
else
    print_error "❌ $services_failed service(s) failed testing"
    echo
    print_info "Troubleshooting:"
    echo "  • Check logs: $DOCKER_COMPOSE_CMD logs"
    echo "  • Check container status: $DOCKER_COMPOSE_CMD ps"
    echo "  • Restart services: $DOCKER_COMPOSE_CMD restart"
    echo "  • View specific service logs: $DOCKER_COMPOSE_CMD logs [service_name]"
fi

echo
print_info "Testing completed!"

# Option to keep containers running or stop them
echo
read -p "Do you want to keep the containers running? (Y/n): " -r
if [[ $REPLY =~ ^[Nn]$ ]]; then
    print_info "Stopping containers..."
    $DOCKER_COMPOSE_CMD down
    print_status "Containers stopped"
else
    print_info "Containers will continue running"
    print_info "Stop them later with: $DOCKER_COMPOSE_CMD down"
fi 