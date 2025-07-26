"""
Basic FSM state operations - setting, clearing, transitions
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from tests.test_utils import setup_test_imports
from tests.base_test_classes import BaseFSMTest
from tests.shared_fixtures import *

# Ensure proper imports
setup_test_imports()

from app.handlers.commands import handle_action_callback
from app.handlers.photo import photo_handler
from common.supabase_client import get_user_with_profile


class NutritionStates(StatesGroup):
    waiting_for_photo = State()


class RecipeStates(StatesGroup):
    waiting_for_photo = State()


class TestFSMBasicOperations(BaseFSMTest):
    """Test basic FSM state operations"""
    
    @pytest.mark.asyncio
    async def test_analyze_button_sets_correct_state(self, state, mock_callback, mock_user_data):
        """Test that analyze button sets nutrition analysis state"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data):
            # Ensure no state is set initially
            await state.clear()
            assert await state.get_state() is None
            
            # Call analyze button
            mock_callback.data = "action_analyze_info"
            await handle_action_callback(mock_callback, state)
            
            # Verify nutrition analysis state was set
            current_state = await state.get_state()
            assert current_state == "NutritionStates:waiting_for_photo"

    @pytest.mark.asyncio
    async def test_recipe_button_sets_correct_state(self, state, mock_callback, mock_user_data):
        """Test that recipe button sets recipe generation state"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data):
            # Ensure no state is set initially
            await state.clear()
            assert await state.get_state() is None
            
            # Call recipe button
            mock_callback.data = "action_recipe"
            await handle_action_callback(mock_callback, state)
            
            # Verify recipe generation state was set
            current_state = await state.get_state()
            assert current_state == "RecipeStates:waiting_for_photo"

    @pytest.mark.asyncio
    async def test_cancel_button_clears_state(self, state, mock_callback, mock_user_data):
        """Test that cancel button clears any active state"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data):
            # Set nutrition analysis state
            await state.set_state(NutritionStates.waiting_for_photo)
            assert await state.get_state() == "NutritionStates:waiting_for_photo"
            
            # Call cancel button
            mock_callback.data = "action_cancel"
            await handle_action_callback(mock_callback, state)
            
            # Verify state was cleared
            final_state = await state.get_state()
            assert final_state is None

    @pytest.mark.asyncio
    async def test_back_button_clears_state(self, state, mock_callback, mock_user_data):
        """Test that back button clears any active state"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data):
            # Set recipe generation state
            await state.set_state(RecipeStates.waiting_for_photo)
            assert await state.get_state() == "RecipeStates:waiting_for_photo"
            
            # Call back button
            mock_callback.data = "action_back"
            await handle_action_callback(mock_callback, state)
            
            # Verify state was cleared
            final_state = await state.get_state()
            assert final_state is None

    @pytest.mark.asyncio
    async def test_main_menu_clears_state(self, state, mock_callback, mock_user_data):
        """Test that main menu clears any active state"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data):
            # Set nutrition analysis state
            await state.set_state(NutritionStates.waiting_for_photo)
            current_state = await state.get_state()
            assert current_state == "NutritionStates:waiting_for_photo"
            
            # Call main menu to exit state
            mock_callback.data = "main_menu"
            await handle_action_callback(mock_callback, state)
            
            # Verify state was cleared
            final_state = await state.get_state()
            assert final_state is None

    @pytest.mark.asyncio
    async def test_state_transition_flow(self, state, mock_callback, mock_user_data):
        """Test complete state transition flow"""
        
        with patch('app.handlers.commands.get_user_with_profile', return_value=mock_user_data):
            # 1. Start with no state
            await state.clear()
            assert await state.get_state() is None
            
            # 2. Enter nutrition analysis state
            mock_callback.data = "action_analyze_info"
            await handle_action_callback(mock_callback, state)
            assert await state.get_state() == "NutritionStates:waiting_for_photo"
            
            # 3. Exit to main menu
            mock_callback.data = "main_menu"
            await handle_action_callback(mock_callback, state)
            assert await state.get_state() is None
            
            # 4. Enter recipe generation state
            mock_callback.data = "action_recipe"
            await handle_action_callback(mock_callback, state)
            assert await state.get_state() == "RecipeStates:waiting_for_photo"
            
            # 5. Exit to main menu
            mock_callback.data = "main_menu"
            await handle_action_callback(mock_callback, state)
            assert await state.get_state() is None