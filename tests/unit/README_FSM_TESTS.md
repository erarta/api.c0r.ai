# FSM State Management Tests

## Overview

This test suite provides comprehensive testing for the Telegram bot's Finite State Machine (FSM) state management system. It ensures that the bot correctly handles state transitions, photo processing, and user interactions.

## Test Coverage

### Core State Management Tests

#### 1. **test_state_setting_and_clearing**
- **Purpose**: Tests basic state setting and clearing operations
- **Scenarios**:
  - Initial state is `None`
  - Setting nutrition analysis state
  - Clearing state returns to `None`
- **Expected**: State transitions work correctly

#### 2. **test_recipe_state_setting_and_clearing**
- **Purpose**: Tests recipe generation state management
- **Scenarios**:
  - Setting recipe generation state
  - Clearing recipe state
- **Expected**: Recipe states work independently from nutrition states

#### 3. **test_state_transitions**
- **Purpose**: Tests transitions between different states
- **Scenarios**:
  - No state → Nutrition analysis → Recipe generation → No state
- **Expected**: Smooth transitions between all states

#### 4. **test_multiple_state_operations**
- **Purpose**: Tests multiple state operations in sequence
- **Scenarios**:
  - Multiple set/clear operations
  - Switching between different states
- **Expected**: State operations are consistent and reliable

### State Persistence and Data Tests

#### 5. **test_state_persistence**
- **Purpose**: Tests that state persists across operations
- **Scenarios**:
  - State remains consistent across multiple checks
  - State is properly cleared when requested
- **Expected**: State persistence works correctly

#### 6. **test_state_data_operations**
- **Purpose**: Tests state data storage and retrieval
- **Scenarios**:
  - Setting state data
  - Updating existing data
  - Preserving data across updates
  - Clearing data with state
- **Expected**: State data operations work correctly

### State Validation Tests

#### 7. **test_state_validation_logic**
- **Purpose**: Tests state validation logic used in handlers
- **Scenarios**:
  - Nutrition state validation
  - Recipe state validation
  - No state validation
- **Expected**: State validation correctly identifies current state

### User Flow Simulation Tests

#### 8. **test_state_flow_simulation**
- **Purpose**: Simulates complete user interaction flows
- **Scenarios**:
  1. User starts with no state
  2. User clicks "Analyze Food" → sets nutrition state
  3. User sends photo → processes → clears state
  4. User clicks "Create Recipe" → sets recipe state
  5. User sends photo → processes → clears state
  6. User clicks "Main Menu" → no state change
- **Expected**: Complete user flows work correctly

### Error Handling Tests

#### 9. **test_error_recovery_state_clearing**
- **Purpose**: Tests state clearing during error recovery
- **Scenarios**:
  - Error occurs during processing
  - State is cleared even after error
- **Expected**: State is properly cleared even when errors occur

### Concurrency Tests

#### 10. **test_concurrent_state_operations**
- **Purpose**: Tests state operations under concurrent access
- **Scenarios**:
  - Multiple concurrent state checks
  - State consistency under load
- **Expected**: State operations are thread-safe

## Running the Tests

### Prerequisites
- Python 3.10+
- pytest
- pytest-asyncio
- aiogram 3.x

### Command
```bash
# Run all FSM tests
python -m pytest tests/unit/test_fsm_state_management_simple.py -v

# Run specific test
python -m pytest tests/unit/test_fsm_state_management_simple.py::TestFSMStateManagementSimple::test_state_flow_simulation -v

# Run with coverage
python -m pytest tests/unit/test_fsm_state_management_simple.py --cov=app.handlers --cov-report=html
```

## Test Structure

### Fixtures
- **bot**: Mock bot instance
- **storage**: Memory storage for FSM
- **dp**: Dispatcher with memory storage
- **state**: FSM context for testing
- **mock_user**: Mock user object
- **mock_chat**: Mock chat object
- **mock_message**: Mock message with photo
- **mock_callback**: Mock callback query

### State Classes
```python
class NutritionStates(StatesGroup):
    waiting_for_photo = State()

class RecipeStates(StatesGroup):
    waiting_for_photo = State()
```

## What These Tests Validate

### 1. **State Management Correctness**
- States are set correctly when buttons are clicked
- States are cleared after photo processing
- States are cleared when users navigate away

### 2. **Photo Processing Flow**
- Photos are processed correctly in nutrition analysis state
- Photos are processed correctly in recipe generation state
- Photos show choice menu when no state is set

### 3. **User Experience**
- Users can seamlessly switch between analysis and recipe modes
- State transitions are smooth and predictable
- Error recovery doesn't leave users in broken states

### 4. **System Reliability**
- State operations are consistent and reliable
- Concurrent operations don't corrupt state
- Error handling properly cleans up state

## Integration with Real Handlers

These tests validate the core FSM logic that the real handlers use:

### Nutrition Analysis Flow
1. User clicks "🍕 Анализ еды" → `NutritionStates.waiting_for_photo`
2. User sends photo → `process_nutrition_analysis()` called
3. Analysis completes → State cleared
4. User returns to main menu

### Recipe Generation Flow
1. User clicks "🍽️ Создать рецепт" → `RecipeStates.waiting_for_photo`
2. User sends photo → `process_recipe_photo()` called
3. Recipe generated → State cleared
4. User returns to main menu

### Default Photo Behavior
1. User sends photo without state → Choice menu shown
2. User can choose analysis or recipe
3. Appropriate state is set based on choice

## Benefits

### 1. **Regression Prevention**
- Catches FSM-related bugs before they reach production
- Ensures state management changes don't break existing functionality

### 2. **Development Confidence**
- Developers can refactor FSM logic with confidence
- New features can be tested against existing state management

### 3. **Documentation**
- Tests serve as living documentation of expected behavior
- New team members can understand FSM flows through tests

### 4. **Debugging**
- Failed tests help identify specific state management issues
- Tests provide clear examples of correct state transitions

## Future Enhancements

### Potential Additional Tests
1. **Integration Tests**: Test with real handlers and mocked external services
2. **Performance Tests**: Test state operations under high load
3. **Edge Case Tests**: Test unusual state transition scenarios
4. **Multi-User Tests**: Test state management with multiple concurrent users

### Test Data Expansion
1. **More Mock Responses**: Add more realistic ML service responses
2. **Error Scenarios**: Test various error conditions and recovery
3. **User Profiles**: Test with different user profile configurations

## Maintenance

### When to Update Tests
- When adding new FSM states
- When changing state transition logic
- When modifying photo processing flows
- When updating error handling

### Test Naming Convention
- Use descriptive names that explain the scenario being tested
- Include expected outcome in test name
- Group related tests in the same class

### Documentation Updates
- Update this README when adding new test categories
- Document any new test patterns or conventions
- Keep examples current with actual implementation 