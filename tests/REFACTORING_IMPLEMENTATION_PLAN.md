# 🛠️ Test Refactoring Implementation Plan

**Target**: Fix critical test issues and improve maintainability  
**Timeline**: 2 weeks  
**Priority**: High (blocks deployment pipeline)

---

## 🎯 Phase 1: Critical File Refactoring (Days 1-3)

### **Task 1.1: Split test_fsm_state_management.py**

**Current Issue**: 534 lines exceeds 500-line limit

**Solution**: Split into 4 focused files:

#### **File 1: test_fsm_basic_operations.py** (~120 lines)
```python
"""
Basic FSM state operations - setting, clearing, transitions
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class NutritionStates(StatesGroup):
    waiting_for_photo = State()

class RecipeStates(StatesGroup):
    waiting_for_photo = State()

class TestFSMBasicOperations:
    """Test basic FSM state operations"""
    
    @pytest_asyncio.fixture
    async def state(self):
        # Proper FSM context setup
        pass
    
    @pytest.mark.asyncio
    async def test_state_setting_and_clearing(self, state):
        # Basic state operations
        pass
    
    @pytest.mark.asyncio
    async def test_state_transitions(self, state):
        # State transition logic
        pass
```

#### **File 2: test_fsm_nutrition_flow.py** (~150 lines)
```python
"""
FSM nutrition analysis workflow tests
"""
# Nutrition-specific FSM tests
```

#### **File 3: test_fsm_recipe_flow.py** (~150 lines)
```python
"""
FSM recipe generation workflow tests
"""
# Recipe-specific FSM tests
```

#### **File 4: test_fsm_error_handling.py** (~100 lines)
```python
"""
FSM error handling and edge cases
"""
# Error scenarios and edge cases
```

**Implementation Steps:**
1. Create new files with proper structure
2. Move related tests to appropriate files
3. Ensure all fixtures are properly shared
4. Run tests to verify no functionality lost
5. Delete original large file

---

## 🔧 Phase 2: AsyncMock Configuration Fix (Days 4-5)

### **Task 2.1: Fix FSM Test Fixtures**

**Current Issue**: `TypeError: object MagicMock can't be used in 'await' expression`

**Root Cause**: Incorrect async fixture configuration

#### **❌ Current Problematic Code:**
```python
@pytest.fixture
async def bot(self):
    return AsyncMock(spec=Bot)  # Wrong: async fixture returning AsyncMock

@pytest.fixture
async def state(self, dp, bot):
    storage_key = StorageKey(
        bot_id=bot.id,  # bot.id is MagicMock, not awaitable
        chat_id=123456789,
        user_id=391490
    )
    return FSMContext(storage=dp.storage, key=storage_key)
```

#### **✅ Fixed Code:**
```python
@pytest.fixture
def mock_bot(self):
    """Create properly configured bot mock"""
    bot = AsyncMock(spec=Bot)
    bot.id = 12345  # Set as property, not mock
    return bot

@pytest_asyncio.fixture
async def state(self, dp, mock_bot):
    """Create FSM context with proper async handling"""
    from aiogram.fsm.storage.base import StorageKey
    storage_key = StorageKey(
        bot_id=mock_bot.id,  # Now this is a real value
        chat_id=123456789,
        user_id=391490
    )
    return FSMContext(storage=dp.storage, key=storage_key)

@pytest_asyncio.fixture
async def dp(self):
    """Create dispatcher with memory storage"""
    from aiogram import Dispatcher
    from aiogram.fsm.storage.memory import MemoryStorage
    return Dispatcher(storage=MemoryStorage())
```

### **Task 2.2: Update All FSM-Related Tests**

**Files to Update:**
- `test_fsm_basic_operations.py`
- `test_fsm_nutrition_flow.py`
- `test_fsm_recipe_flow.py`
- `test_fsm_error_handling.py`
- `test_recipe_fsm_states.py`

**Standard Fixture Pattern:**
```python
# shared_fixtures.py (new file)
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

@pytest.fixture
def mock_bot():
    bot = AsyncMock(spec=Bot)
    bot.id = 12345
    return bot

@pytest_asyncio.fixture
async def storage():
    return MemoryStorage()

@pytest_asyncio.fixture
async def dp(storage):
    return Dispatcher(storage=storage)

@pytest_asyncio.fixture
async def state(dp, mock_bot):
    storage_key = StorageKey(
        bot_id=mock_bot.id,
        chat_id=123456789,
        user_id=391490
    )
    return FSMContext(storage=dp.storage, key=storage_key)
```

---

## 📁 Phase 3: Import Path Standardization (Days 6-7)

### **Task 3.1: Create Standard Import Helper**

**Create**: `tests/test_utils.py`
```python
"""
Shared utilities for test imports and setup
"""
import sys
import os

def setup_test_imports():
    """Standard import path setup for all tests"""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Add specific paths if needed
    api_path = os.path.join(project_root, 'api.c0r.ai')
    if api_path not in sys.path:
        sys.path.insert(0, api_path)

# Call this at module level in each test file
setup_test_imports()
```

### **Task 3.2: Update All Test Files**

**Replace this pattern in all test files:**
```python
# ❌ Remove this
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api.c0r.ai'))

# ✅ Replace with this
from tests.test_utils import setup_test_imports
setup_test_imports()
```

**Files to Update:**
- All files in `tests/unit/`
- All files in `tests/integration/`

---

## 🧪 Phase 4: Test Structure Optimization (Days 8-10)

### **Task 4.1: Create Shared Test Base Classes**

**Create**: `tests/base_test_classes.py`
```python
"""
Base test classes with common functionality
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, CallbackQuery, User, Chat, PhotoSize

class BaseHandlerTest:
    """Base class for handler tests"""
    
    @pytest.fixture
    def mock_user(self):
        user = MagicMock(spec=User)
        user.id = 391490
        user.username = "testuser"
        user.language_code = "ru"
        return user
    
    @pytest.fixture
    def mock_chat(self):
        chat = MagicMock(spec=Chat)
        chat.id = 123456789
        chat.type = "private"
        return chat
    
    @pytest.fixture
    def mock_message(self, mock_user, mock_chat):
        message = MagicMock(spec=Message)
        message.from_user = mock_user
        message.chat = mock_chat
        message.message_id = 123
        message.answer = AsyncMock()
        return message
    
    @pytest.fixture
    def mock_callback(self, mock_user, mock_chat):
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = mock_user
        callback.message = MagicMock(spec=Message)
        callback.message.chat = mock_chat
        callback.answer = AsyncMock()
        return callback

class BaseFSMTest(BaseHandlerTest):
    """Base class for FSM-related tests"""
    
    @pytest.fixture
    def mock_user_data(self):
        return {
            'user': {
                'id': 'd4047507-274c-493c-99b5-af801a5b7195',
                'telegram_id': 391490,
                'credits_remaining': 25,
                'language': 'ru'
            },
            'profile': {
                'age': 38,
                'gender': 'male',
                'height_cm': 170,
                'weight_kg': 69.0,
                'activity_level': 'moderately_active',
                'goal': 'maintain_weight'
            },
            'has_profile': True
        }
```

### **Task 4.2: Update Test Classes to Inherit from Base**

**Example Update:**
```python
# ❌ Before
class TestFSMBasicOperations:
    @pytest.fixture
    def mock_user(self):
        # Duplicate fixture code
        pass

# ✅ After
from tests.base_test_classes import BaseFSMTest

class TestFSMBasicOperations(BaseFSMTest):
    # Inherits all common fixtures
    pass
```

---

## 🔗 Phase 5: Integration Test Fixes (Days 11-12)

### **Task 5.1: Environment Configuration**

**Create**: `tests/.env.test`
```bash
# Test environment variables
SUPABASE_URL=http://localhost:54321
SUPABASE_SERVICE_ROLE_KEY=test_key
YOOKASSA_SHOP_ID=test_shop_id
YOOKASSA_SECRET_KEY=test_secret_key
ML_SERVICE_URL=http://localhost:8001
TELEGRAM_BOT_TOKEN=test_token
```

**Update**: `tests/conftest.py`
```python
"""
Global test configuration
"""
import os
import pytest
from dotenv import load_dotenv

# Load test environment
load_dotenv('tests/.env.test')

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment variables"""
    os.environ.setdefault('ENVIRONMENT', 'test')
    os.environ.setdefault('SUPABASE_URL', 'http://localhost:54321')
    # Set other test defaults
```

### **Task 5.2: Mock External Services**

**Create**: `tests/mocks/external_services.py`
```python
"""
Mock external services for integration tests
"""
from unittest.mock import AsyncMock, MagicMock

class MockSupabaseClient:
    def __init__(self):
        self.table = MagicMock()
        self.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    
    def from_(self, table_name):
        return self.table()

class MockYooKassaClient:
    def __init__(self):
        self.payment = MagicMock()
    
    async def create_payment(self, amount, currency, description):
        return {
            'id': 'test_payment_id',
            'status': 'pending',
            'confirmation': {
                'confirmation_url': 'https://test.yookassa.ru/payments/test'
            }
        }
```

---

## 📊 Phase 6: Validation and Testing (Days 13-14)

### **Task 6.1: Run Complete Test Suite**

**Commands to Execute:**
```bash
# Run all unit tests
python -m pytest tests/unit/ -v --tb=short

# Run all integration tests
python -m pytest tests/integration/ -v --tb=short

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html --cov-report=term

# Check for any remaining issues
python -m pytest tests/ --tb=no -q
```

### **Task 6.2: Verify Refactoring Success**

**Success Criteria:**
- [ ] All test files ≤ 500 lines
- [ ] No AsyncMock-related errors
- [ ] All import paths working
- [ ] Test coverage maintained or improved
- [ ] All tests passing locally

### **Task 6.3: Update Documentation**

**Update**: `tests/README.md`
```markdown
# Test Suite Documentation

## Structure
- `unit/` - Unit tests (isolated functionality)
- `integration/` - Integration tests (external services)
- `base_test_classes.py` - Shared test base classes
- `test_utils.py` - Common utilities
- `conftest.py` - Global test configuration

## Running Tests
```bash
# All tests
python -m pytest tests/

# Unit tests only
python -m pytest tests/unit/

# Integration tests only
python -m pytest tests/integration/

# With coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## Best Practices
1. Keep test files under 500 lines
2. Use shared fixtures from base classes
3. Proper AsyncMock configuration for async tests
4. Standard import path setup
```

---

## 🎯 Implementation Checklist

### **Week 1: Core Refactoring**
- [ ] **Day 1**: Split `test_fsm_state_management.py` into 4 files
- [ ] **Day 2**: Create and test new file structure
- [ ] **Day 3**: Verify all tests still pass after split
- [ ] **Day 4**: Fix AsyncMock configuration in all FSM tests
- [ ] **Day 5**: Create shared fixtures and base classes
- [ ] **Day 6**: Standardize import paths across all files
- [ ] **Day 7**: Create test utilities and helpers

### **Week 2: Integration and Validation**
- [ ] **Day 8**: Update integration tests with proper mocking
- [ ] **Day 9**: Configure test environment variables
- [ ] **Day 10**: Create external service mocks
- [ ] **Day 11**: Run complete test suite validation
- [ ] **Day 12**: Fix any remaining issues
- [ ] **Day 13**: Update documentation
- [ ] **Day 14**: Final validation and sign-off

---

## 🚀 Expected Outcomes

### **Immediate Benefits**
1. **Compliance**: All test files under 500-line limit
2. **Reliability**: No more AsyncMock-related failures
3. **Maintainability**: Standardized structure and imports
4. **Speed**: Faster test execution with proper mocking

### **Long-term Benefits**
1. **Scalability**: Easy to add new tests following established patterns
2. **Debugging**: Clear separation of concerns makes issues easier to trace
3. **Collaboration**: Consistent structure improves team productivity
4. **CI/CD**: Reliable tests enable automated deployment pipeline

---

## 📞 Support and Resources

### **Implementation Support**
- **Code Reviews**: Available for each phase
- **Pair Programming**: Available for complex refactoring
- **Testing**: Help with validation and edge cases

### **Documentation**
- **Best Practices**: Detailed testing guidelines
- **Examples**: Reference implementations for common patterns
- **Troubleshooting**: Common issues and solutions

---

**Plan prepared by**: Kilo Code  
**Ready for implementation**: ✅  
**Estimated effort**: 14 days (2 developers)  
**Risk level**: Low (incremental changes with validation)