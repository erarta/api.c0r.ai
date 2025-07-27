# Deployment with Mandatory Testing

## 🎯 Overview
Starting with v0.3.10, all deployments **must pass comprehensive tests** before proceeding to production. This ensures code quality and prevents broken features from reaching users.

## 🚀 Deployment Process

### 1. Local Deployment
```bash
# Full deployment with testing
./scripts/deploy.sh

# The script will:
# 1. Pull latest changes
# 2. Run comprehensive tests (MANDATORY)
# 3. If tests pass: deploy to production
# 4. If tests fail: BLOCK deployment
```

### 2. GitHub Actions Deployment
```bash
# Push to main branch triggers:
git push origin main

# GitHub Actions will:
# 1. Run test job (unit + integration + coverage)
# 2. Only deploy if ALL tests pass
# 3. Upload coverage reports
```

## 🧪 Testing Structure

### Tests Organization
```
tests/
├── unit/                    # Unit tests (with coverage)
│   ├── test_nutrition.py
│   ├── test_commands.py
│   └── test_nutrition_calculations.py
├── integration/             # Integration tests
│   ├── test_api_integration.py      # Internal API tests
│   ├── test_db_connection.py        # Database connection
│   ├── test_bot_connection.py       # Telegram bot
│   ├── test_payment_simple.py      # Payment system
│   ├── test_telegram_payments.py   # Telegram payments
│   └── test_yookassa_integration.py # YooKassa integration
├── run_tests.py             # Main test runner
├── run_integration_tests.py # External integration tests
└── deploy_test.sh           # Deployment test script
```

### Test Runners
```bash
# Run all tests (unit + integration + coverage)
cd tests && python run_tests.py

# Run only external integration tests
cd tests && python run_integration_tests.py

# Run deployment tests (what deploy.sh uses)
./tests/deploy_test.sh
```

## 📊 Test Requirements

### Coverage Requirements
- **Minimum**: 85% code coverage
- **Critical files**: Must have >85% coverage:
  - `handlers/nutrition.py`
  - `handlers/commands.py`
  - `common/nutrition_calculations.py`
  - `common/supabase_client.py`

### Test Categories
1. **Unit Tests**: Fast, isolated component tests
2. **Integration Tests**: Database, API, external services
3. **Critical Path Tests**: Bug-specific regression tests

## 🔒 Deployment Protection

### Automatic Blocking
Deployment is **automatically blocked** if:
- Any unit test fails
- Any integration test fails
- Code coverage is below 85%
- Critical bug regression tests fail

### Manual Override (Emergency Only)
```bash
# Emergency deployment (use only for critical fixes)
export EMERGENCY_DEPLOY=true
./scripts/deploy.sh
```

## 🛠️ Development Workflow

### Before Committing
```bash
# Run tests locally
cd tests && python run_tests.py

# Check specific critical paths
./tests/deploy_test.sh
```

### Before Pushing
```bash
# Ensure all tests pass
./tests/deploy_test.sh

# If tests pass, safe to push
git push origin main
```

## 📋 Test Maintenance

### Adding New Tests
1. Add unit tests in `tests/unit/`
2. Add integration tests in `tests/integration/`
3. Update `run_tests.py` if needed
4. Ensure coverage meets requirements

### Test Dependencies
```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Dependencies include:
# - pytest, pytest-cov, pytest-asyncio
# - requests, yookassa, aiogram
# - supabase, python-dotenv
```

## 🚨 Troubleshooting

### Common Issues

**Tests fail locally but pass in CI:**
- Check Python version (use 3.10+)
- Verify environment variables
- Install all dependencies

**Coverage below 85%:**
- Add missing test cases
- Check uncovered code paths
- Remove dead code

**Integration tests fail:**
- Verify external service credentials
- Check network connectivity
- Ensure test data is available

### Getting Help
1. Check test output for specific errors
2. Review coverage reports in `tests/coverage/`
3. Run individual test files for debugging
4. Check CHANGELOG.md for recent changes

## 🎉 Benefits

### Production Safety
- **Zero broken deployments**: Tests catch issues before production
- **Regression protection**: Previous bugs can't resurface
- **Quality assurance**: Consistent code quality standards

### Development Speed
- **Confidence**: Deploy knowing code works
- **Fast feedback**: Catch issues early
- **Documentation**: Tests serve as living documentation

### Team Collaboration
- **Standards**: Consistent quality across all contributors
- **Review**: Pull requests include test results
- **Monitoring**: Coverage trends track code health

---

**Remember**: Tests are not optional - they're a deployment requirement! 🧪✅ 