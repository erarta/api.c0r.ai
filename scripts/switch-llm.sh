#!/bin/bash

# Script to switch LLM providers for C0R.AI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_usage() {
    echo -e "${BLUE}Usage: $0 <provider>${NC}"
    echo ""
    echo -e "${YELLOW}Available providers:${NC}"
    echo "  openai     - OpenAI GPT-4o (high accuracy, reliable)"
    echo "  perplexity - Perplexity Sonar (supports vision, online search)"
    echo "  gemini     - Google Gemini (alternative option)"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 perplexity"
    echo "  $0 openai"
}

if [ $# -eq 0 ]; then
    print_usage
    exit 1
fi

PROVIDER="$1"

# Validate provider
case $PROVIDER in
    "openai"|"perplexity"|"gemini")
        echo -e "${GREEN}✓ Valid provider: $PROVIDER${NC}"
        ;;
    *)
        echo -e "${RED}❌ Invalid provider: $PROVIDER${NC}"
        print_usage
        exit 1
        ;;
esac

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# Get current provider
CURRENT_PROVIDER=$(grep "^LLM_PROVIDER=" .env | cut -d'=' -f2)
echo -e "${BLUE}🔄 Current provider: ${CURRENT_PROVIDER:-'not set'}${NC}"

# Update .env file
if grep -q "^LLM_PROVIDER=" .env; then
    # Replace existing line
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/^LLM_PROVIDER=.*/LLM_PROVIDER=$PROVIDER/" .env
    else
        # Linux
        sed -i "s/^LLM_PROVIDER=.*/LLM_PROVIDER=$PROVIDER/" .env
    fi
else
    # Add new line
    echo "LLM_PROVIDER=$PROVIDER" >> .env
fi

echo -e "${GREEN}✓ Updated .env: LLM_PROVIDER=$PROVIDER${NC}"

# Restart ML service to apply changes
echo -e "${YELLOW}🔄 Restarting ML service...${NC}"
if docker-compose restart ml > /dev/null 2>&1; then
    echo -e "${GREEN}✓ ML service restarted${NC}"
    
    # Wait for service to be ready
    echo -e "${YELLOW}⏳ Waiting for service to be ready...${NC}"
    sleep 10
    
    # Verify the change
    ACTUAL_PROVIDER=$(curl -s http://localhost:8001/health 2>/dev/null | jq -r '.current_llm_provider' 2>/dev/null)
    
    if [ "$ACTUAL_PROVIDER" = "$PROVIDER" ]; then
        echo -e "${GREEN}🎉 Successfully switched to: $PROVIDER${NC}"
        
        # Show additional info
        echo ""
        echo -e "${BLUE}📊 Current Status:${NC}"
        curl -s http://localhost:8001/health | jq '{
            current_llm_provider: .current_llm_provider,
            available_providers: .available_providers,
            status: .status
        }' 2>/dev/null || echo "Could not fetch status"
        
    else
        echo -e "${YELLOW}⚠️  Provider set to $PROVIDER but service shows: $ACTUAL_PROVIDER${NC}"
        echo -e "${YELLOW}💡 This might be due to API key availability or fallback logic${NC}"
    fi
    
else
    echo -e "${RED}❌ Failed to restart ML service${NC}"
    echo -e "${YELLOW}💡 Try: docker-compose restart ml${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🚀 Ready to test! Send a food photo to see $PROVIDER in action.${NC}" 