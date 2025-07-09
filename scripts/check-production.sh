#!/bin/bash

# Production Health Check Script for c0r.ai
# Usage: ./scripts/check-production.sh

set -e

echo "🚀 c0r.ai Production Health Check"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
else
    echo -e "${RED}❌ .env.production file not found${NC}"
    exit 1
fi

# Function to check URL
check_url() {
    local url=$1
    local name=$2
    
    echo -n "🔍 Checking $name... "
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200"; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

# Function to check service health
check_service_health() {
    local url=$1
    local name=$2
    
    echo -n "🏥 Checking $name health... "
    
    response=$(curl -s "$url/health" 2>/dev/null || echo "ERROR")
    
    if echo "$response" | grep -q "healthy"; then
        echo -e "${GREEN}✅ HEALTHY${NC}"
        return 0
    else
        echo -e "${RED}❌ UNHEALTHY${NC}"
        echo "   Response: $response"
        return 1
    fi
}

# Function to check Telegram bot
check_telegram_bot() {
    echo -n "🤖 Checking Telegram bot... "
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
        echo -e "${RED}❌ TELEGRAM_BOT_TOKEN not set${NC}"
        return 1
    fi
    
    response=$(curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe" 2>/dev/null || echo "ERROR")
    
    if echo "$response" | grep -q '"ok":true'; then
        bot_username=$(echo "$response" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}✅ OK (@$bot_username)${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

# Function to check Docker containers
check_docker_containers() {
    echo "🐳 Checking Docker containers..."
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker not installed${NC}"
        return 1
    fi
    
    containers=("api" "ml" "pay")
    all_running=true
    
    for container in "${containers[@]}"; do
        echo -n "   $container: "
        if docker ps --format "table {{.Names}}" | grep -q "api.c0r.ai-$container"; then
            echo -e "${GREEN}✅ RUNNING${NC}"
        else
            echo -e "${RED}❌ NOT RUNNING${NC}"
            all_running=false
        fi
    done
    
    return $all_running
}

# Function to check SSL certificates
check_ssl_certificates() {
    echo "🔒 Checking SSL certificates..."
    
    domains=("api.c0r.ai" "ml.c0r.ai" "pay.c0r.ai")
    
    for domain in "${domains[@]}"; do
        echo -n "   $domain: "
        
        cert_info=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
        
        if [ $? -eq 0 ]; then
            expiry=$(echo "$cert_info" | grep "notAfter" | cut -d= -f2)
            echo -e "${GREEN}✅ Valid (expires: $expiry)${NC}"
        else
            echo -e "${RED}❌ INVALID${NC}"
        fi
    done
}

# Function to test YooKassa webhook
test_webhook() {
    echo -n "🪝 Testing YooKassa webhook... "
    
    response=$(curl -s -X POST "https://pay.c0r.ai/webhook/yookassa" \
        -H "Content-Type: application/json" \
        -d '{
            "type": "payment.succeeded",
            "event": "payment.succeeded",
            "object": {
                "id": "test_payment_id",
                "status": "succeeded",
                "amount": {"value": "99.00", "currency": "RUB"},
                "metadata": {"telegram_user_id": "123456", "plan": "basic", "credits": "20"}
            }
        }' 2>/dev/null || echo "ERROR")
    
    if echo "$response" | grep -q '"status":"ok"'; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "   Response: $response"
        return 1
    fi
}

# Main checks
echo "1. 🌐 Service Availability"
echo "========================="
check_url "https://api.c0r.ai" "API Service"
check_url "https://ml.c0r.ai" "ML Service"
check_url "https://pay.c0r.ai" "Payment Service"
echo ""

echo "2. 🏥 Service Health"
echo "==================="
check_service_health "https://api.c0r.ai" "API Service"
check_service_health "https://ml.c0r.ai" "ML Service"
check_service_health "https://pay.c0r.ai" "Payment Service"
echo ""

echo "3. 🤖 Telegram Bot"
echo "=================="
check_telegram_bot
echo ""

echo "4. 🐳 Docker Containers"
echo "======================="
check_docker_containers
echo ""

echo "5. 🔒 SSL Certificates"
echo "======================"
check_ssl_certificates
echo ""

echo "6. 🪝 Webhook Testing"
echo "===================="
test_webhook
echo ""

echo "7. 📊 System Resources"
echo "======================"
echo "💾 Disk usage:"
df -h | grep -E "(Filesystem|/dev/)"
echo ""
echo "🧠 Memory usage:"
free -h
echo ""
echo "📈 Docker stats:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo ""

echo "8. 🔍 Recent Logs"
echo "================="
echo "📋 Last 5 lines from each service:"
echo ""
echo "API Service:"
docker logs api.c0r.ai-api-1 --tail 5 2>/dev/null || echo "No logs available"
echo ""
echo "ML Service:"
docker logs api.c0r.ai-ml-1 --tail 5 2>/dev/null || echo "No logs available"
echo ""
echo "Payment Service:"
docker logs api.c0r.ai-pay-1 --tail 5 2>/dev/null || echo "No logs available"
echo ""

echo "=================================="
echo "🎯 Production Health Check Complete"
echo "=================================="
echo ""
echo "📝 Next steps:"
echo "1. Test payment flow in Telegram (@c0rAIBot)"
echo "2. Send test photo for analysis"
echo "3. Monitor logs for any errors"
echo "4. Check YooKassa dashboard for test payments"
echo ""
echo "🆘 If any checks failed, see PRODUCTION_TESTING_GUIDE.md" 