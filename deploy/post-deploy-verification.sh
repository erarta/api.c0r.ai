#!/bin/bash
# Post-deployment Verification Script for Enhanced Nutrition System
# Verifies that all enhanced features are working correctly after deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
API_URL="${API_URL:-http://localhost:8000}"
DATABASE_URL="${DATABASE_URL:-postgresql://postgres.cadeererdjwemspkeriq:xuoO4|LSaaGX5@aws-0-eu-north-1.pooler.supabase.com:6543/postgres}"
TIMEOUT=30

# Counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅ $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ❌ $1${NC}"
    ((TESTS_FAILED++))
}

warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠️  $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')] ℹ️  $1${NC}"
}

test_start() {
    ((TESTS_TOTAL++))
    info "Testing: $1"
}

test_pass() {
    ((TESTS_PASSED++))
    log "$1"
}

# Test helper function
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="${3:-0}"

    test_start "$test_name"

    if eval "$test_command" >/dev/null 2>&1; then
        if [ "$expected_result" = "0" ]; then
            test_pass "$test_name - PASSED"
        else
            error "$test_name - FAILED (expected failure but succeeded)"
        fi
    else
        if [ "$expected_result" != "0" ]; then
            test_pass "$test_name - PASSED (expected failure)"
        else
            error "$test_name - FAILED"
        fi
    fi
}

# HTTP test helper
test_endpoint() {
    local name="$1"
    local endpoint="$2"
    local expected_status="${3:-200}"
    local method="${4:-GET}"

    test_start "$name"

    local response_code
    if [ "$method" = "GET" ]; then
        response_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $TIMEOUT "$API_URL$endpoint" 2>/dev/null || echo "000")
    else
        response_code=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" --connect-timeout $TIMEOUT "$API_URL$endpoint" 2>/dev/null || echo "000")
    fi

    if [ "$response_code" = "$expected_status" ]; then
        test_pass "$name - Status $response_code"
    else
        error "$name - Expected $expected_status, got $response_code"
    fi
}

# Database test helper
test_db_query() {
    local name="$1"
    local query="$2"
    local expected_min_count="${3:-1}"

    test_start "$name"

    if ! command -v python3 >/dev/null 2>&1; then
        error "$name - Python 3 not available for database testing"
        return
    fi

    local result
    result=$(python3 -c "
import psycopg2
import sys

try:
    conn = psycopg2.connect('$DATABASE_URL')
    cur = conn.cursor()
    cur.execute(\"$query\")
    result = cur.fetchone()[0] if cur.rowcount > 0 else 0
    conn.close()
    print(result)
except Exception as e:
    print(0)
    sys.exit(1)
" 2>/dev/null)

    if [ "$result" -ge "$expected_min_count" ]; then
        test_pass "$name - Found $result records"
    else
        error "$name - Expected at least $expected_min_count records, found $result"
    fi
}

echo ""
echo "🚀 Starting Enhanced Nutrition System Verification"
echo "=================================================="
echo "API URL: $API_URL"
echo "Timestamp: $(date)"
echo "=================================================="
echo ""

# Basic API Health Tests
info "🔍 Testing Basic API Health..."
test_endpoint "Basic Health Check" "/health" 200
test_endpoint "API Root Response" "/" 200

# Enhanced Nutrition API Tests
info "🧬 Testing Enhanced Nutrition Endpoints..."
test_endpoint "Nutrition DNA Health" "/health/nutrition-dna" 200
test_endpoint "Nutrition System Health" "/health/nutrition-system" 200
test_endpoint "Questionnaire Summary" "/nutrition-onboarding/questionnaire-summary" 200

# Database Schema Verification
info "🗄️  Verifying Database Schema..."
test_db_query "Schema Migrations Table" "SELECT COUNT(*) FROM schema_migrations WHERE status = 'applied'" 1
test_db_query "Nutrition DNA Table" "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'nutrition_dna'" 1
test_db_query "Meal Recommendations Table" "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'meal_recommendations'" 1
test_db_query "Questionnaire Responses Table" "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'nutrition_questionnaire_responses'" 1
test_db_query "Enhanced Analysis Table" "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'user_food_analysis_enhanced'" 1

# User Profiles Enhancement Verification
info "👤 Verifying User Profiles Enhancements..."
test_db_query "Onboarding Completed Column" "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'onboarding_completed'" 1
test_db_query "Favorite Foods Column" "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'favorite_foods'" 1
test_db_query "Cooking Skill Column" "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'cooking_skill'" 1
test_db_query "Social Eating Column" "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'user_profiles' AND column_name = 'social_eating_frequency'" 1

# Meal Plans Enhancement Verification
info "🍽️  Verifying Meal Plans Enhancements..."
test_db_query "Nutrition DNA Reference" "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'meal_plans' AND column_name = 'nutrition_dna_id'" 1
test_db_query "Personalization Level Column" "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'meal_plans' AND column_name = 'personalization_level'" 1

# Index Verification
info "📊 Verifying Database Indexes..."
test_db_query "Nutrition DNA User Index" "SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'nutrition_dna' AND indexname LIKE '%user_id%'" 1
test_db_query "User Profiles Onboarding Index" "SELECT COUNT(*) FROM pg_indexes WHERE tablename = 'user_profiles' AND indexname LIKE '%onboarding%'" 1

# Views Verification
info "👁️  Verifying Database Views..."
test_db_query "Complete Nutrition Profiles View" "SELECT COUNT(*) FROM information_schema.views WHERE table_name = 'complete_nutrition_profiles'" 1
test_db_query "Recent Recommendations View" "SELECT COUNT(*) FROM information_schema.views WHERE table_name = 'recent_meal_recommendations'" 1

# Feature Flag Tests (if available)
if [ ! -z "$USE_ENHANCED_AI" ] && [ "$USE_ENHANCED_AI" = "true" ]; then
    info "🎛️  Enhanced AI Features Enabled"
    test_pass "Enhanced AI feature flag is active"
else
    warning "Enhanced AI features may be disabled"
fi

# Performance Tests (basic)
info "⚡ Testing Performance..."
start_time=$(date +%s%N)
test_endpoint "Quick Response Test" "/health" 200
end_time=$(date +%s%N)
response_time=$(( (end_time - start_time) / 1000000 ))  # Convert to milliseconds

if [ $response_time -lt 1000 ]; then
    test_pass "Response Time - ${response_time}ms (excellent)"
elif [ $response_time -lt 3000 ]; then
    test_pass "Response Time - ${response_time}ms (good)"
else
    warning "Response Time - ${response_time}ms (may need optimization)"
fi

# Integration Tests (if test data exists)
info "🔗 Testing Integration..."
if [ ! -z "$TEST_USER_ID" ]; then
    # Test with actual user data if available
    test_db_query "Test User Nutrition Data" "SELECT COUNT(*) FROM user_profiles WHERE user_id = '$TEST_USER_ID'" 1
else
    info "Skipping integration tests (TEST_USER_ID not set)"
fi

# Final Summary
echo ""
echo "=================================================="
echo "🎯 VERIFICATION SUMMARY"
echo "=================================================="
echo "Tests Total:  $TESTS_TOTAL"
echo "Tests Passed: $TESTS_PASSED"
echo "Tests Failed: $TESTS_FAILED"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ ALL TESTS PASSED - Enhanced Nutrition System is working correctly!${NC}"
    echo ""
    echo "🚀 Deployment verified successfully!"
    echo "🧬 Enhanced nutrition features are operational"
    echo "📊 Database schema is correctly updated"
    echo "🎯 All API endpoints are responding"
    echo ""
    echo "Key Features Verified:"
    echo "• Nutrition DNA profiling system"
    echo "• Personalized onboarding questionnaire"
    echo "• Adaptive meal recommendations"
    echo "• Enhanced database schema"
    echo "• API endpoint availability"
    echo ""
    exit 0
else
    echo -e "${RED}❌ $TESTS_FAILED TESTS FAILED - Review issues above${NC}"
    echo ""
    echo "🔍 Common troubleshooting steps:"
    echo "1. Check if all environment variables are set correctly"
    echo "2. Verify database migrations completed successfully"
    echo "3. Ensure application has restarted after deployment"
    echo "4. Check application logs for specific error details"
    echo "5. Verify network connectivity to database and external services"
    echo ""
    echo "📚 For detailed troubleshooting, see: docs/troubleshooting/enhanced-features.md"
    echo ""
    exit 1
fi