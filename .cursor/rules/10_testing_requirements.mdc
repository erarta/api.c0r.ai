# Testing Requirements Rule

## 🧪 Mandatory Testing for All New Functionality

### Core Principle
**EVERY new feature, function, or significant code change MUST have corresponding tests before being considered complete.**

### Testing Requirements

#### 1. **Unit Tests for Functions**
- Every new function must have unit tests covering:
  - ✅ Happy path scenarios (normal inputs)
  - ❌ Error cases and edge cases
  - 🔄 Boundary conditions
  - 📊 Input validation
  - 🎯 Expected output verification

#### 2. **Integration Tests for Features**
- New features interacting with external services must have integration tests:
  - 🌐 API endpoints
  - 🗄️ Database operations
  - 📧 External service calls
  - 🔐 Authentication/authorization flows

#### 3. **Test Organization**
- Place unit tests in: `tests/unit/`
- Place integration tests in: `tests/integration/`
- Use descriptive test file names: `test_[feature_name].py`
- Use descriptive test method names: `test_[functionality]_[scenario]`

#### 4. **Local Testing Requirement**
Before any code is committed or deployed:
```bash
# Must pass locally
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v

# Must meet coverage requirements
python -m pytest tests/ --cov=. --cov-report=html --cov-fail-under=85
```

#### 5. **Deployment Testing Integration**
- All tests are automatically run in CI/CD pipeline
- Deployment is blocked if any tests fail
- Coverage must be ≥85% for deployment to proceed

### Test Structure Template

```python
"""
Test [feature_name] functionality
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class Test[FeatureName]:
    """Test [feature_name] functionality"""
    
    def test_[function]_with_valid_input(self):
        """Test [function] with valid input"""
        # Arrange
        input_data = {...}
        expected_result = {...}
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        assert result == expected_result
        
    def test_[function]_with_invalid_input(self):
        """Test [function] with invalid input"""
        # Should test error handling
        with pytest.raises(ExpectedError):
            function_under_test(invalid_input)
            
    def test_[function]_edge_cases(self):
        """Test [function] with edge cases"""
        # Test boundary conditions, empty inputs, etc.
        pass
```

### Examples of Good Testing

#### ✅ Good Examples:
- `tests/unit/test_nutrition_sanitization.py` - Comprehensive markdown sanitization tests
- `tests/unit/test_nutrition_calculations.py` - BMI, water needs, macro calculations
- `tests/integration/test_telegram_payments.py` - External payment service testing

#### ❌ Bad Examples (Don't Do This):
- Writing code without any tests
- Only testing happy path scenarios
- Skipping error case testing
- Not testing edge cases or boundary conditions
- Writing tests after deployment issues

### Enforcement

#### Pre-Commit Checklist:
- [ ] All new functions have unit tests
- [ ] All new features have integration tests
- [ ] Tests pass locally: `pytest tests/ -v`
- [ ] Coverage is adequate: `pytest tests/ --cov=. --cov-report=term`
- [ ] No critical functionality is untested

#### CI/CD Integration:
- GitHub Actions automatically runs all tests
- Deployment is blocked if tests fail
- Coverage reports are generated and uploaded
- Failed deployments trigger alerts

### Testing Tools Available

#### Local Testing:
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/unit/test_nutrition.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test method
python -m pytest tests/unit/test_nutrition.py::TestClass::test_method -v
```

#### Deployment Testing:
```bash
# Run deployment test suite
./tests/deploy_test.sh

# Run integration tests only
python tests/run_integration_tests.py
```

### Benefits of This Approach

1. **🛡️ Prevents Production Bugs** - Catches issues before they reach users
2. **🔄 Enables Safe Refactoring** - Confidence to improve code
3. **📚 Documents Behavior** - Tests serve as executable documentation
4. **⚡ Faster Development** - Quick feedback on code changes
5. **🎯 Better Code Quality** - Forces thinking about edge cases

### Emergency Exception Process

If absolutely critical hotfix is needed without full test coverage:
1. Deploy with explicit approval and documentation
2. Create follow-up task to add missing tests within 24 hours
3. Test coverage debt must be paid before next feature work

### Remember: Testing is NOT Optional

**Tests are part of the feature, not an afterthought. A feature is not complete until it has proper test coverage.** 