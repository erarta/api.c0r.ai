#!/bin/bash

# c0r.ai API Deployment Test Script
# This script MUST pass before any production deployment

set -e  # Exit on any error

echo "🚀 c0r.ai API Deployment Test Suite"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

echo -e "${YELLOW}📍 Project root: $PROJECT_ROOT${NC}"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ ERROR: docker-compose.yml not found. Make sure you're in the project root.${NC}"
    exit 1
fi

# Function to run command with status check
run_command() {
    local cmd="$1"
    local description="$2"
    
    echo -e "${YELLOW}🔄 $description...${NC}"
    
    if eval "$cmd"; then
        echo -e "${GREEN}✅ $description - SUCCESS${NC}"
        return 0
    else
        echo -e "${RED}❌ $description - FAILED${NC}"
        return 1
    fi
}

# Function to check test results
check_test_results() {
    local test_type="$1"
    local log_file="$2"
    
    if [ -f "$log_file" ]; then
        local failed_tests=$(grep -c "FAILED" "$log_file" 2>/dev/null || echo "0")
        local passed_tests=$(grep -c "PASSED" "$log_file" 2>/dev/null || echo "0")
        
        echo -e "${YELLOW}📊 $test_type Results: $passed_tests passed, $failed_tests failed${NC}"
        
        if [ "$failed_tests" -gt 0 ]; then
            echo -e "${RED}❌ $test_type has failures!${NC}"
            return 1
        else
            echo -e "${GREEN}✅ $test_type all passed!${NC}"
            return 0
        fi
    else
        echo -e "${RED}❌ $test_type log file not found: $log_file${NC}"
        return 1
    fi
}

# Step 1: Install test dependencies
echo -e "\n${YELLOW}📦 Installing test dependencies...${NC}"
if [ -f "tests/requirements.txt" ]; then
    run_command "pip install -r tests/requirements.txt" "Installing test dependencies"
else
    echo -e "${RED}❌ tests/requirements.txt not found${NC}"
    exit 1
fi

# Step 2: Check Python syntax
echo -e "\n${YELLOW}🔍 Checking Python syntax...${NC}"
run_command "python -m py_compile api.c0r.ai/app/config.py" "Checking config.py syntax"
run_command "python -m py_compile api.c0r.ai/app/handlers/nutrition.py" "Checking nutrition.py syntax"
run_command "python -m py_compile api.c0r.ai/app/handlers/commands.py" "Checking commands.py syntax"
run_command "python -m py_compile common/nutrition_calculations.py" "Checking nutrition_calculations.py syntax"

# Step 3: Run critical unit tests
echo -e "\n${YELLOW}🧪 Running critical unit tests...${NC}"
mkdir -p tests/coverage

# Test the nutrition insights bug fix specifically
run_command "python -m pytest tests/unit/test_nutrition.py::TestNutritionInsights::test_nutrition_insights_with_none_profile -v" "Testing nutrition insights None profile fix"

# Test version consistency
run_command "python -m pytest tests/unit/test_commands.py::TestVersionConsistency -v" "Testing version consistency"

# Test nutrition calculations
run_command "python -m pytest tests/unit/test_nutrition_calculations.py::TestCalculateBMI -v" "Testing BMI calculations"

# Step 4: Run integration tests for critical paths
echo -e "\n${YELLOW}🔗 Running critical integration tests...${NC}"
run_command "python -m pytest tests/integration/test_api_integration.py::TestCriticalPathsIntegration -v" "Testing critical paths integration"

# Step 5: Run full test suite with coverage
echo -e "\n${YELLOW}🎯 Running full test suite with coverage...${NC}"
run_command "python tests/run_tests.py" "Full test suite with coverage"

# Step 6: Check coverage report
echo -e "\n${YELLOW}📊 Checking coverage report...${NC}"
if [ -f "tests/coverage/coverage_report.md" ]; then
    echo -e "${GREEN}✅ Coverage report generated${NC}"
    
    # Extract coverage percentage
    if grep -q "PASSED.*Coverage meets minimum requirement" tests/coverage/coverage_report.md; then
        echo -e "${GREEN}✅ Coverage meets 85% requirement${NC}"
    else
        echo -e "${RED}❌ Coverage below 85% requirement${NC}"
        echo -e "${YELLOW}📋 Coverage details:${NC}"
        grep "Total Coverage" tests/coverage/coverage_report.md
        exit 1
    fi
else
    echo -e "${RED}❌ Coverage report not found${NC}"
    exit 1
fi

# Step 7: Test configuration consistency
echo -e "\n${YELLOW}⚙️ Testing configuration consistency...${NC}"
run_command "python -c 'from api.c0r.ai.app.config import VERSION; print(f\"Version: {VERSION}\"); assert VERSION == \"0.3.10\"'" "Checking version configuration"

# Step 8: Test critical imports
echo -e "\n${YELLOW}📥 Testing critical imports...${NC}"
run_command "python -c 'from handlers.nutrition import nutrition_insights_command; print(\"✅ Nutrition imports OK\")'" "Testing nutrition imports"
run_command "python -c 'from handlers.commands import start_command; print(\"✅ Commands imports OK\")'" "Testing commands imports"
run_command "python -c 'from common.nutrition_calculations import calculate_bmi; print(\"✅ Calculations imports OK\")'" "Testing calculations imports"

# Step 9: Test database connection (if available)
echo -e "\n${YELLOW}🗄️ Testing database connection...${NC}"
if [ -f ".env" ]; then
    echo -e "${YELLOW}📋 .env file found, testing database connection...${NC}"
    run_command "python -c 'from common.supabase_client import supabase; print(\"✅ Supabase connection OK\")'" "Testing Supabase connection" || echo -e "${YELLOW}⚠️ Database connection test skipped (likely no credentials)${NC}"
else
    echo -e "${YELLOW}⚠️ No .env file found, skipping database tests${NC}"
fi

# Step 10: Final deployment readiness check
echo -e "\n${YELLOW}🎯 Final deployment readiness check...${NC}"

# Check if all critical files exist
critical_files=(
    "api.c0r.ai/app/config.py"
    "api.c0r.ai/app/handlers/nutrition.py"
    "api.c0r.ai/app/handlers/commands.py"
    "common/nutrition_calculations.py"
    "docker-compose.yml"
    "CHANGELOG.md"
)

for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file exists${NC}"
    else
        echo -e "${RED}❌ $file missing${NC}"
        exit 1
    fi
done

# Final summary
echo -e "\n${'='*50}"
echo -e "${GREEN}🎉 DEPLOYMENT TESTS PASSED!${NC}"
echo -e "${'='*50}"

echo -e "${GREEN}✅ All unit tests passed${NC}"
echo -e "${GREEN}✅ All integration tests passed${NC}"
echo -e "${GREEN}✅ Code coverage ≥ 85%${NC}"
echo -e "${GREEN}✅ Critical bug fixes verified${NC}"
echo -e "${GREEN}✅ Version consistency checked${NC}"
echo -e "${GREEN}✅ All critical files present${NC}"

echo -e "\n${GREEN}🚀 READY FOR PRODUCTION DEPLOYMENT!${NC}"
echo -e "${YELLOW}📋 Coverage report: tests/coverage/combined_html/index.html${NC}"
echo -e "${YELLOW}📋 Test logs: tests/coverage/coverage_report.md${NC}"

exit 0 