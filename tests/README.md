# c0r.ai API Test Suite

Comprehensive testing system for the c0r.ai API to ensure code quality and prevent deployment of broken code.

## 🎯 Testing Strategy

### Critical Bug Coverage
- **Nutrition Insights NoneType Error**: Specifically tests the bug where `profile.get()` was called on `None`
- **Version Consistency**: Ensures version is correctly displayed across all system components
- **Profile Validation**: Tests all profile validation scenarios

### Test Structure
```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_nutrition.py   # Nutrition handler tests (critical)
│   ├── test_commands.py    # Commands handler tests
│   └── test_nutrition_calculations.py  # Calculation engine tests
├── integration/            # Integration tests for component interaction
│   └── test_api_integration.py  # Full API integration tests
├── coverage/               # Coverage reports (generated)
├── run_tests.py           # Main test runner with coverage
├── deploy_test.sh         # Deployment readiness test script
└── requirements.txt       # Test dependencies
```

## 🚀 Running Tests

### Quick Test Run
```bash
# Run all tests with coverage
python tests/run_tests.py
```

### Specific Test Categories
```bash
# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only  
python -m pytest tests/integration/ -v

# Critical nutrition tests
python -m pytest tests/unit/test_nutrition.py -v

# Version consistency tests
python -m pytest tests/unit/test_commands.py::TestVersionConsistency -v
```

### Deployment Test Suite
```bash
# Run full deployment readiness test
chmod +x tests/deploy_test.sh
./tests/deploy_test.sh
```

## 📊 Coverage Requirements

- **Minimum Coverage**: 85%
- **Critical Components**: Must have >85% coverage
  - `handlers/nutrition.py` (nutrition insights)
  - `handlers/commands.py` (core commands)
  - `common/nutrition_calculations.py` (calculation engine)
  - `common/supabase_client.py` (database operations)

### Coverage Reports
- **HTML Report**: `tests/coverage/combined_html/index.html`
- **JSON Report**: `tests/coverage/combined_coverage.json`
- **Markdown Report**: `tests/coverage/coverage_report.md`

## 🛡️ Deployment Protection

### Pre-deployment Checks
The `deploy_test.sh` script MUST pass before any production deployment:

1. **Syntax Check**: Validates Python syntax
2. **Critical Tests**: Runs bug-specific tests
3. **Integration Tests**: Tests component interaction
4. **Coverage Check**: Ensures ≥85% coverage
5. **Version Consistency**: Validates version display
6. **Import Tests**: Checks all imports work
7. **File Existence**: Verifies critical files present

### CI/CD Integration
```yaml
# Example GitHub Actions step
- name: Run Deployment Tests
  run: |
    chmod +x tests/deploy_test.sh
    ./tests/deploy_test.sh
```

## 🧪 Test Categories

### Unit Tests
- **TestNutritionInsights**: Tests nutrition insights functionality
  - `test_nutrition_insights_with_none_profile` - Critical bug fix
  - `test_nutrition_insights_with_empty_profile` - Edge case
  - `test_nutrition_insights_with_partial_profile` - Partial data
  - `test_nutrition_insights_with_complete_profile` - Happy path

- **TestCommands**: Tests command handlers
  - `test_status_command_with_version` - Version display
  - `test_start_command_new_user` - New user flow
  - `test_handle_action_callback` - Button interactions

- **TestNutritionCalculations**: Tests calculation engine
  - `test_bmi_*` - BMI calculations for all categories
  - `test_water_needs_*` - Water requirement calculations
  - `test_macro_distribution_*` - Macro nutrient distribution

### Integration Tests
- **TestUserJourney**: Complete user flows
  - `test_new_user_complete_flow` - New user experience
  - `test_existing_user_with_profile_flow` - Existing user with profile

- **TestCriticalPaths**: Critical bug scenarios
  - `test_nutrition_insights_critical_path` - Exact bug scenario from logs
  - `test_user_with_profile_critical_path` - Working user scenario

## 🔧 Test Development

### Adding New Tests
1. Create test file in appropriate directory (`unit/` or `integration/`)
2. Follow naming convention: `test_*.py`
3. Use descriptive test names: `test_specific_functionality`
4. Include docstrings explaining test purpose
5. Mock external dependencies
6. Test both success and failure scenarios

### Test Structure
```python
class TestComponentName:
    """Test suite for component functionality"""
    
    @pytest.mark.asyncio
    async def test_specific_functionality(self):
        """Test specific functionality with detailed description"""
        # Arrange
        setup_mocks()
        
        # Act
        result = await function_under_test()
        
        # Assert
        assert expected_result == result
```

### Mocking Guidelines
- Mock external dependencies (database, API calls)
- Use `AsyncMock` for async functions
- Mock at the appropriate level (not too deep)
- Verify mocks are called correctly

## 📋 Test Maintenance

### Version Updates
When updating version in `config.py`:
1. Update version-related tests
2. Update expected version in deployment script
3. Run full test suite to ensure consistency

### Adding New Features
1. Write tests first (TDD approach)
2. Ensure critical paths are tested
3. Add integration tests for complex interactions
4. Update coverage requirements if needed

### Bug Fixes
1. Create failing test that reproduces the bug
2. Fix the bug
3. Ensure test now passes
4. Add additional edge case tests

## 🚨 Common Issues

### Test Failures
- **Import Errors**: Check Python path setup in test files
- **Mock Issues**: Ensure mocks are patched at correct location
- **Async Issues**: Use `@pytest.mark.asyncio` for async tests
- **Coverage Low**: Add tests for uncovered code paths

### Deployment Failures
- **Syntax Errors**: Fix Python syntax issues
- **Missing Dependencies**: Install test requirements
- **Version Mismatch**: Update version in config.py
- **Coverage Below 85%**: Add more tests or improve existing ones

## 💡 Best Practices

1. **Test Independence**: Tests should not depend on each other
2. **Clear Naming**: Use descriptive test and function names
3. **Documentation**: Include docstrings for complex tests
4. **Edge Cases**: Test boundary conditions and error scenarios
5. **Mock Appropriately**: Mock external dependencies, not internal logic
6. **Maintain Coverage**: Keep coverage above 85%
7. **Update Tests**: Update tests when functionality changes

## 📞 Support

If you encounter issues with the test suite:
1. Check this README for common solutions
2. Review test logs for specific error messages
3. Ensure all dependencies are installed
4. Contact the development team for assistance

## 🔄 Continuous Improvement

The test suite is continuously improved to:
- Catch more bugs before deployment
- Improve coverage of critical paths
- Reduce test execution time
- Enhance test reliability
- Better integration with CI/CD pipelines

Remember: **All tests must pass before production deployment!** 