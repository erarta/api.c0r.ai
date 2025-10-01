#!/bin/bash
# Script to validate production config before deployment
# Added by Claude to prevent config overwrites

set -e

echo "🔍 Validating production configuration..."

# Required production environment variables
REQUIRED_PROD_VARS=(
    "TELEGRAM_BOT_TOKEN"
    "SUPABASE_URL"
    "SUPABASE_SERVICE_KEY"
    "INTERNAL_API_TOKEN"
    "API_PUBLIC_URL"
    "BYPASS_SUBSCRIPTION"
    "ENVIRONMENT"
)

# Check if production .env exists
if [ ! -f ".env" ]; then
    echo "❌ Production .env file not found!"
    exit 1
fi

# Validate required variables
missing_vars=()
for var in "${REQUIRED_PROD_VARS[@]}"; do
    if ! grep -q "^${var}=" .env; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo "❌ Missing required production variables:"
    printf '%s\n' "${missing_vars[@]}"
    exit 1
fi

# Check if using production bot token (not test token)
if grep -q "7981950009" .env; then
    echo "❌ Using test bot token in production!"
    exit 1
fi

# Check if using production database
if ! grep -q "mmrzpngugivxoapjiovb" .env; then
    echo "❌ Not using production Supabase database!"
    exit 1
fi

echo "✅ Production configuration validated successfully!"
echo "📋 Current configuration summary:"
echo "   Bot Token: $(grep TELEGRAM_BOT_TOKEN .env | cut -d'=' -f2 | cut -c1-20)..."
echo "   Database: $(grep SUPABASE_URL .env | cut -d'/' -f3)"
echo "   Environment: $(grep ENVIRONMENT .env | cut -d'=' -f2)"
echo "   Bypass Subscription: $(grep BYPASS_SUBSCRIPTION .env | cut -d'=' -f2)"