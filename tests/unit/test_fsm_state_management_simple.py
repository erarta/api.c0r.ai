"""
Simplified FSM State Management Tests

This test suite focuses on core FSM state transitions and logic
without complex external dependencies.
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, User, Chat, PhotoSize
from aiogram.fsm.state import State, StatesGroup


class NutritionStates(StatesGroup):
    waiting_for_photo = State()


class RecipeStates(StatesGroup):
    waiting_for_photo = State()


class TestFSMStateManagementSimple:
    """Simplified FSM state management test suite"""
    
    @pytest_asyncio.fixture
    async def bot(self):
        """Create a mock bot instance"""
        return AsyncMock(spec=Bot)
    
    @pytest_asyncio.fixture
    async def storage(self):
        """Create a memory storage for FSM"""
        return MemoryStorage()
    
    @pytest_asyncio.fixture
    async def dp(self, storage):
        """Create a dispatcher with memory storage"""
        return Dispatcher(storage=storage)
    
    @pytest_asyncio.fixture
    async def state(self, dp, bot):
        """Create FSM context"""
        from aiogram.fsm.storage.base import StorageKey
        storage_key = StorageKey(
            bot_id=bot.id,
            chat_id=123456789,
            user_id=391490
        )
        return FSMContext(storage=dp.storage, key=storage_key)
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user"""
        user = MagicMock(spec=User)
        user.id = 391490
        user.username = "testuser"
        return user
    
    @pytest.fixture
    def mock_chat(self):
        """Create a mock chat"""
        chat = MagicMock(spec=Chat)
        chat.id = 123456789
        chat.type = "private"
        return chat
    
    @pytest.fixture
    def mock_message(self, mock_user, mock_chat):
        """Create a mock message"""
        message = MagicMock(spec=Message)
        message.from_user = mock_user
        message.chat = mock_chat
        message.message_id = 123
        
        # Mock photo
        photo = MagicMock(spec=PhotoSize)
        photo.file_id = "test_file_id"
        photo.file_size = 50000
        message.photo = [photo]
        
        return message
    
    @pytest.fixture
    def mock_callback(self, mock_user, mock_chat):
        """Create a mock callback query"""
        callback = MagicMock(spec=CallbackQuery)
        callback.from_user = mock_user
        callback.message.chat = mock_chat
        callback.message.message_id = 123
        callback.data = "action_analyze_info"
        return callback

    @pytest.mark.asyncio
    async def test_state_setting_and_clearing(self, state):
        """Test basic state setting and clearing"""
        
        # Test initial state is None
        initial_state = await state.get_state()
        assert initial_state is None
        
        # Set nutrition analysis state
        await state.set_state(NutritionStates.waiting_for_photo)
        current_state = await state.get_state()
        assert current_state == "NutritionStates:waiting_for_photo"
        
        # Clear state
        await state.clear()
        final_state = await state.get_state()
        assert final_state is None

    @pytest.mark.asyncio
    async def test_recipe_state_setting_and_clearing(self, state):
        """Test recipe state setting and clearing"""
        
        # Test initial state is None
        initial_state = await state.get_state()
        assert initial_state is None
        
        # Set recipe generation state
        await state.set_state(RecipeStates.waiting_for_photo)
        current_state = await state.get_state()
        assert current_state == "RecipeStates:waiting_for_photo"
        
        # Clear state
        await state.clear()
        final_state = await state.get_state()
        assert final_state is None

    @pytest.mark.asyncio
    async def test_state_transitions(self, state):
        """Test state transitions between different states"""
        
        # Start with no state
        await state.clear()
        assert await state.get_state() is None
        
        # Transition to nutrition analysis
        await state.set_state(NutritionStates.waiting_for_photo)
        assert await state.get_state() == "NutritionStates:waiting_for_photo"
        
        # Transition to recipe generation
        await state.set_state(RecipeStates.waiting_for_photo)
        assert await state.get_state() == "RecipeStates:waiting_for_photo"
        
        # Clear state
        await state.clear()
        assert await state.get_state() is None

    @pytest.mark.asyncio
    async def test_multiple_state_operations(self, state):
        """Test multiple state operations in sequence"""
        
        # Test multiple set/clear operations
        await state.set_state(NutritionStates.waiting_for_photo)
        assert await state.get_state() == "NutritionStates:waiting_for_photo"
        
        await state.clear()
        assert await state.get_state() is None
        
        await state.set_state(RecipeStates.waiting_for_photo)
        assert await state.get_state() == "RecipeStates:waiting_for_photo"
        
        await state.clear()
        assert await state.get_state() is None
        
        await state.set_state(NutritionStates.waiting_for_photo)
        assert await state.get_state() == "NutritionStates:waiting_for_photo"

    @pytest.mark.asyncio
    async def test_state_persistence(self, state):
        """Test that state persists across operations"""
        
        # Set state
        await state.set_state(NutritionStates.waiting_for_photo)
        
        # Check state multiple times
        for _ in range(5):
            current_state = await state.get_state()
            assert current_state == "NutritionStates:waiting_for_photo"
        
        # Clear state
        await state.clear()
        
        # Check state is cleared
        for _ in range(5):
            current_state = await state.get_state()
            assert current_state is None

    @pytest.mark.asyncio
    async def test_state_data_operations(self, state):
        """Test state data operations"""
        
        # Set state and data
        await state.set_state(NutritionStates.waiting_for_photo)
        await state.update_data(user_id=391490, action="nutrition_analysis")
        
        # Verify state and data
        current_state = await state.get_state()
        data = await state.get_data()
        
        assert current_state == "NutritionStates:waiting_for_photo"
        assert data["user_id"] == 391490
        assert data["action"] == "nutrition_analysis"
        
        # Update data
        await state.update_data(credits=25)
        data = await state.get_data()
        assert data["credits"] == 25
        assert data["user_id"] == 391490  # Previous data preserved
        
        # Clear state
        await state.clear()
        data = await state.get_data()
        assert data == {}

    @pytest.mark.asyncio
    async def test_state_validation_logic(self, state):
        """Test state validation logic"""
        
        # Test nutrition analysis state validation
        await state.set_state(NutritionStates.waiting_for_photo)
        current_state = await state.get_state()
        
        # Simulate state validation logic
        is_nutrition_state = current_state == "NutritionStates:waiting_for_photo"
        is_recipe_state = current_state == "RecipeStates:waiting_for_photo"
        has_state = current_state is not None
        
        assert is_nutrition_state is True
        assert is_recipe_state is False
        assert has_state is True
        
        # Test recipe state validation
        await state.set_state(RecipeStates.waiting_for_photo)
        current_state = await state.get_state()
        
        is_nutrition_state = current_state == "NutritionStates:waiting_for_photo"
        is_recipe_state = current_state == "RecipeStates:waiting_for_photo"
        has_state = current_state is not None
        
        assert is_nutrition_state is False
        assert is_recipe_state is True
        assert has_state is True
        
        # Test no state validation
        await state.clear()
        current_state = await state.get_state()
        
        is_nutrition_state = current_state == "NutritionStates:waiting_for_photo"
        is_recipe_state = current_state == "RecipeStates:waiting_for_photo"
        has_state = current_state is not None
        
        assert is_nutrition_state is False
        assert is_recipe_state is False
        assert has_state is False

    @pytest.mark.asyncio
    async def test_state_flow_simulation(self, state):
        """Simulate complete user flow with state management"""
        
        # 1. User starts with no state
        await state.clear()
        assert await state.get_state() is None
        
        # 2. User clicks "Analyze Food" button
        await state.set_state(NutritionStates.waiting_for_photo)
        assert await state.get_state() == "NutritionStates:waiting_for_photo"
        
        # 3. User sends photo (simulate processing)
        # State should be cleared after processing
        await state.clear()
        assert await state.get_state() is None
        
        # 4. User clicks "Create Recipe" button
        await state.set_state(RecipeStates.waiting_for_photo)
        assert await state.get_state() == "RecipeStates:waiting_for_photo"
        
        # 5. User sends photo (simulate processing)
        # State should be cleared after processing
        await state.clear()
        assert await state.get_state() is None
        
        # 6. User clicks "Main Menu" (no state change needed)
        assert await state.get_state() is None

    @pytest.mark.asyncio
    async def test_error_recovery_state_clearing(self, state):
        """Test that state is properly cleared even after errors"""
        
        # Set state
        await state.set_state(NutritionStates.waiting_for_photo)
        assert await state.get_state() == "NutritionStates:waiting_for_photo"
        
        # Simulate error during processing
        try:
            # Simulate some error
            raise Exception("Processing error")
        except Exception:
            # State should be cleared even after error
            await state.clear()
        
        # Verify state was cleared
        final_state = await state.get_state()
        assert final_state is None

    @pytest.mark.asyncio
    async def test_concurrent_state_operations(self, state):
        """Test concurrent state operations"""
        
        # Set initial state
        await state.set_state(NutritionStates.waiting_for_photo)
        
        # Simulate concurrent operations
        async def check_state():
            return await state.get_state()
        
        # Run multiple concurrent state checks
        tasks = [check_state() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should return the same state
        for result in results:
            assert result == "NutritionStates:waiting_for_photo"
        
        # Clear state
        await state.clear()
        
        # Run multiple concurrent state checks after clearing
        tasks = [check_state() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should return None
        for result in results:
            assert result is None 