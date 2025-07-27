# Test Suite Documentation

## 🧪 Overview

This test suite provides comprehensive coverage for the c0r.AI nutrition analysis bot, including unit tests, integration tests, and end-to-end testing scenarios.

## 📁 Structure

```
tests/
├── unit/                       # Unit tests (isolated functionality)
│   ├── test_fsm_basic_operations.py    # FSM state transitions
│   ├── test_fsm_nutrition_flow.py      # Nutrition analysis workflow
│   ├── test_fsm_recipe_flow.py         # Recipe generation workflow
│   ├── test_fsm_error_handling.py      # FSM error scenarios
│   ├── test_nutrition_calculations.py   # Nutrition calculations
│   ├── test_nutrition_sanitization.py  # Markdown sanitization
│   ├── test_recipe_fsm_states.py       # Recipe FSM states
│   └── ...
├── integration/                # Integration tests (external services)
│   ├── test_api_integration.py         # API endpoint testing
│   ├── test_telegram_payments.py       # Payment integration
│   ├── test_yookassa_integration.py    # YooKassa payment tests
│   └── ...
├── shared_fixtures.py          # Shared test fixtures
├── base_test_classes.py        # Base test classes
├── test_utils.py              # Common utilities
├── conftest.py                # Global test configuration
└── .env.test                  # Test environment variables
```

## 🚀 Running Tests

### All Tests
```bash
python -m pytest tests/
```

### Unit Tests Only
```bash
python -m pytest tests/unit/
```

### Integration Tests Only
```bash
python -m pytest tests/integration/
```

### With Coverage
```bash
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term
```

### Specific Test File
```bash
python -m pytest tests/unit/test_nutrition_calculations.py -v
```

### Specific Test Method
```bash
python -m pytest tests/unit/test_fsm_basic_operations.py::TestFSMBasicOperations::test_analyze_button_sets_correct_state -v
```

## 🏗️ Test Architecture

### Shared Components

#### Base Test Classes
- **`BaseHandlerTest`**: Common fixtures for handler testing
- **`BaseFSMTest`**: FSM-specific test functionality
- **`BaseIntegrationTest`**: Integration test utilities

#### Shared Fixtures
- **`mock_bot`**: Properly configured bot mock
- **`state`**: FSM context with memory storage
- **`mock_user_data`**: Standard user profile data
- **`mock_ml_response`**: ML service response mock
- **`mock_recipe_response`**: Recipe generation response mock

#### Test Utilities
- **`setup_test_imports()`**: Standardized import path configuration
- **Environment setup**: Test-specific environment variables

### FSM Test Structure

The FSM (Finite State Machine) tests are organized into focused modules:

1. **Basic Operations** (`test_fsm_basic_operations.py`)
   - State setting and clearing
   - Button interactions
   - State transitions

2. **Nutrition Flow** (`test_fsm_nutrition_flow.py`)
   - Nutrition analysis workflow
   - Photo processing
   - ML service integration

3. **Recipe Flow** (`test_fsm_recipe_flow.py`)
   - Recipe generation workflow
   - Dietary preferences handling
   - Error scenarios

4. **Error Handling** (`test_fsm_error_handling.py`)
   - Exception handling
   - Edge cases
   - Recovery scenarios

## 🔧 Configuration

### Environment Variables
Test environment is configured via `tests/.env.test`:
```bash
SUPABASE_URL=http://localhost:54321
SUPABASE_SERVICE_ROLE_KEY=test_key
YOOKASSA_SHOP_ID=test_shop_id
YOOKASSA_SECRET_KEY=test_secret_key
ML_SERVICE_URL=http://localhost:8001
TELEGRAM_BOT_TOKEN=test_token
ENVIRONMENT=test
```

### Pytest Configuration
Settings in `tests/pytest.ini`:
- Async test support
- Custom markers
- Warning filters
- Test discovery patterns

## 📊 Coverage Targets

- **Overall Coverage**: ≥85%
- **Critical Paths**: 100%
- **FSM Logic**: 100%
- **Nutrition Calculations**: 100%

## 🧪 Test Categories

### Unit Tests
- **Nutrition Calculations**: BMI, water needs, macro distribution
- **Message Formatting**: Markdown sanitization, text processing
- **FSM State Management**: State transitions, error handling
- **Profile Management**: User onboarding, profile updates

### Integration Tests
- **API Endpoints**: Health checks, analysis endpoints
- **External Services**: ML service, payment processing
- **Database Operations**: User data, transaction logging
- **Bot Integration**: Telegram API, webhook handling

## 🔍 Best Practices

### Test Structure
1. **Arrange-Act-Assert** pattern
2. **Descriptive test names** explaining what is being tested
3. **Single responsibility** per test method
4. **Proper mocking** of external dependencies

### Fixture Usage
```python
from tests.base_test_classes import BaseFSMTest
from tests.shared_fixtures import *

class TestMyFeature(BaseFSMTest):
    @pytest.mark.asyncio
    async def test_feature_behavior(self, state, mock_user_data):
        # Test implementation
        pass
```

### Import Standardization
```python
from tests.test_utils import setup_test_imports

# Ensure proper imports
setup_test_imports()

# Import application modules
from app.handlers.photo import photo_handler
```

## 🐛 Debugging Tests

### Common Issues
1. **Import Errors**: Ensure `setup_test_imports()` is called
2. **AsyncMock Issues**: Use proper async fixtures
3. **State Management**: Clear FSM state between tests
4. **Mock Configuration**: Verify mock return values

### Debug Commands
```bash
# Run with detailed output
python -m pytest tests/unit/test_fsm_basic_operations.py -v -s

# Run with pdb on failure
python -m pytest tests/unit/test_fsm_basic_operations.py --pdb

# Run specific test with coverage
python -m pytest tests/unit/test_nutrition_calculations.py::TestCalculateBMI::test_bmi_normal_weight --cov=common.nutrition_calculations --cov-report=term-missing
```

## 📈 Continuous Integration

### Pre-commit Checks
- All tests must pass
- Coverage threshold must be met
- No linting errors
- Import paths standardized

### Deployment Pipeline
- Unit tests run on every commit
- Integration tests run on pull requests
- Full test suite runs before deployment
- Coverage reports generated and uploaded

## 🔄 Maintenance

### Adding New Tests
1. Choose appropriate test category (unit/integration)
2. Use existing base classes and fixtures
3. Follow naming conventions
4. Ensure proper mocking
5. Update documentation if needed

### Updating Existing Tests
1. Maintain backward compatibility
2. Update related fixtures if needed
3. Verify all dependent tests still pass
4. Update coverage expectations

## 📞 Support

For test-related issues:
1. Check this documentation
2. Review existing test patterns
3. Verify environment setup
4. Check import paths and fixtures

---

**Last Updated**: 2025-07-26  
**Test Framework**: pytest 8.2.0  
**Python Version**: 3.13+  
**Coverage Target**: 85%