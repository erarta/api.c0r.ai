#!/bin/bash

# Script to switch between development and production environment configurations
# Usage: ./scripts/switch-env.sh [dev|prod]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

ENV_MODE="${1:-dev}"

case $ENV_MODE in
    "dev"|"development")
        echo "🔧 Switching to development environment..."
        
        # Update service URLs in .env for local Docker
        if [ -f "$ROOT_DIR/.env" ]; then
            # Backup current .env
            cp "$ROOT_DIR/.env" "$ROOT_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"
            
            # Update service URLs for local development
            sed -i.bak 's|ML_SERVICE_URL=https://ml\.c0r\.ai|ML_SERVICE_URL=http://ml:8001|g' "$ROOT_DIR/.env"
            sed -i.bak 's|PAY_SERVICE_URL=https://pay\.c0r\.ai|PAY_SERVICE_URL=http://pay:8002|g' "$ROOT_DIR/.env"
            
            # Remove backup file created by sed
            rm -f "$ROOT_DIR/.env.bak"
            
            echo "✅ Development environment configured"
            echo "   ML_SERVICE_URL=http://ml:8001"
            echo "   PAY_SERVICE_URL=http://pay:8002"
        else
            echo "❌ .env file not found. Please copy from .env.example first"
            exit 1
        fi
        ;;
        
    "prod"|"production")
        echo "🚀 Switching to production environment..."
        
        # Update service URLs in .env for production subdomains
        if [ -f "$ROOT_DIR/.env" ]; then
            # Backup current .env
            cp "$ROOT_DIR/.env" "$ROOT_DIR/.env.backup.$(date +%Y%m%d_%H%M%S)"
            
            # Update service URLs for production
            sed -i.bak 's|ML_SERVICE_URL=http://ml:8001|ML_SERVICE_URL=https://ml.c0r.ai|g' "$ROOT_DIR/.env"
            sed -i.bak 's|PAY_SERVICE_URL=http://pay:8002|PAY_SERVICE_URL=https://pay.c0r.ai|g' "$ROOT_DIR/.env"
            
            # Remove backup file created by sed
            rm -f "$ROOT_DIR/.env.bak"
            
            echo "✅ Production environment configured"
            echo "   ML_SERVICE_URL=https://ml.c0r.ai"
            echo "   PAY_SERVICE_URL=https://pay.c0r.ai"
            
            echo ""
            echo "⚠️  Make sure you have:"
            echo "   1. DNS records pointing api/ml/pay.c0r.ai to your AWS EC2 IP"
            echo "   2. SSL certificates configured"
            echo "   3. All production secrets set in .env"
        else
            echo "❌ .env file not found. Please copy from .env.production.example first"
            exit 1
        fi
        ;;
        
    *)
        echo "❌ Invalid environment mode: $ENV_MODE"
        echo "Usage: $0 [dev|prod]"
        echo ""
        echo "Examples:"
        echo "  $0 dev   # Switch to development (Docker internal URLs)"
        echo "  $0 prod  # Switch to production (AWS subdomain URLs)"
        exit 1
        ;;
esac

echo ""
echo "🔍 Current service URLs in .env:"
grep -E "^(ML_SERVICE_URL|PAY_SERVICE_URL)" "$ROOT_DIR/.env" || echo "No service URLs found" 