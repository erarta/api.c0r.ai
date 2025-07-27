#!/bin/bash

# 🚀 Real-time Bot Monitoring Script for c0r.ai
# Usage: ./monitor_bot.sh [mode]
# Modes: logs, errors, users, performance, all

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}🚀 c0r.ai Bot Monitor${NC}"
    echo -e "${BLUE}================================${NC}"
}

monitor_logs() {
    echo -e "${GREEN}📊 Monitoring all bot logs...${NC}"
    docker-compose logs -f api | while read line; do
        if echo "$line" | grep -q "ERROR"; then
            echo -e "${RED}[ERROR] $line${NC}"
        elif echo "$line" | grep -q "WARNING"; then
            echo -e "${YELLOW}[WARNING] $line${NC}"
        elif echo "$line" | grep -q "INFO"; then
            echo -e "${GREEN}[INFO] $line${NC}"
        else
            echo "$line"
        fi
    done
}

monitor_errors() {
    echo -e "${RED}🚨 Monitoring ERRORS only...${NC}"
    docker-compose logs -f api | grep -E "(ERROR|EXCEPTION|Failed|Error)" --color=always
}

monitor_users() {
    echo -e "${BLUE}👥 Monitoring user activity...${NC}"
    docker-compose logs -f api | grep -E "(user_|telegram_user_id|New user|Photo analysis)" --color=always
}

monitor_performance() {
    echo -e "${YELLOW}⚡ Performance monitoring...${NC}"
    while true; do
        echo -e "${BLUE}[$(date)] System Status:${NC}"
        echo -e "${GREEN}Memory Usage:${NC}"
        docker stats --no-stream api.c0r.ai-api-1 2>/dev/null || echo "Container not running"
        echo -e "${GREEN}Disk Usage:${NC}"
        df -h / | tail -1
        echo -e "${GREEN}Active Connections:${NC}"
        netstat -an | grep :8000 | wc -l
        echo "---"
        sleep 10
    done
}

monitor_all() {
    echo -e "${BLUE}🔍 Comprehensive monitoring...${NC}"
    
    # Start background monitoring
    (monitor_performance > performance.log 2>&1 &)
    
    # Monitor logs with filters
    docker-compose logs -f api | while read line; do
        timestamp=$(date '+%H:%M:%S')
        
        if echo "$line" | grep -q "ERROR"; then
            echo -e "${RED}[$timestamp] [ERROR] $line${NC}"
        elif echo "$line" | grep -q "WARNING"; then
            echo -e "${YELLOW}[$timestamp] [WARNING] $line${NC}"
        elif echo "$line" | grep -q "user_"; then
            echo -e "${BLUE}[$timestamp] [USER] $line${NC}"
        elif echo "$line" | grep -q "photo"; then
            echo -e "${GREEN}[$timestamp] [PHOTO] $line${NC}"
        elif echo "$line" | grep -q "profile"; then
            echo -e "${BLUE}[$timestamp] [PROFILE] $line${NC}"
        elif echo "$line" | grep -q "rate_limit"; then
            echo -e "${YELLOW}[$timestamp] [RATE_LIMIT] $line${NC}"
        else
            echo "[$timestamp] $line"
        fi
    done
}

show_stats() {
    echo -e "${GREEN}📈 Current Statistics:${NC}"
    echo "---"
    
    # Check if container is running
    if ! docker-compose ps | grep -q "Up"; then
        echo -e "${RED}❌ Bot containers not running!${NC}"
        return 1
    fi
    
    # Get recent stats from logs
    echo -e "${BLUE}Recent Activity (last 100 lines):${NC}"
    
    LOGS=$(docker-compose logs --tail=100 api 2>/dev/null)
    
    PHOTO_COUNT=$(echo "$LOGS" | grep "Photo analysis completed" | wc -l)
    PROFILE_COUNT=$(echo "$LOGS" | grep "Profile created" | wc -l)
    ERROR_COUNT=$(echo "$LOGS" | grep "ERROR" | wc -l)
    USER_COUNT=$(echo "$LOGS" | grep "New user registered" | wc -l)
    
    echo -e "${GREEN}✅ Photo analyses: $PHOTO_COUNT${NC}"
    echo -e "${GREEN}✅ Profile setups: $PROFILE_COUNT${NC}"
    echo -e "${GREEN}✅ New users: $USER_COUNT${NC}"
    echo -e "${RED}❌ Errors: $ERROR_COUNT${NC}"
    
    echo "---"
    echo -e "${BLUE}System Status:${NC}"
    docker-compose ps
}

# Main script
print_header

case "${1:-all}" in
    "logs")
        monitor_logs
        ;;
    "errors")
        monitor_errors
        ;;
    "users")
        monitor_users
        ;;
    "performance")
        monitor_performance
        ;;
    "stats")
        show_stats
        ;;
    "all")
        monitor_all
        ;;
    *)
        echo -e "${YELLOW}Usage: ./monitor_bot.sh [mode]${NC}"
        echo ""
        echo -e "${GREEN}Available modes:${NC}"
        echo "  logs        - All bot logs with colors"
        echo "  errors      - Only errors and exceptions"
        echo "  users       - User activity and interactions"
        echo "  performance - System performance metrics"
        echo "  stats       - Current statistics summary"
        echo "  all         - Comprehensive monitoring (default)"
        echo ""
        echo -e "${BLUE}Examples:${NC}"
        echo "  ./monitor_bot.sh errors"
        echo "  ./monitor_bot.sh users"
        echo "  ./monitor_bot.sh stats"
        ;;
esac 