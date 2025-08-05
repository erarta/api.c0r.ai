"""
Unit tests for CaloriesService module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from decimal import Decimal

from common.calories_service import CaloriesService


class TestCaloriesService:
    """Test cases for CaloriesService"""
    
    @pytest.fixture
    def calories_service(self):
        """Create CaloriesService instance with mocked Supabase client"""
        with patch('common.calories_service.get_supabase_client') as mock_get_client:
            mock_client = Mock()
            mock_get_client.return_value = mock_client
            service = CaloriesService()
            service.supabase = mock_client
            return service
    
    @pytest.fixture
    def mock_supabase_response(self):
        """Mock Supabase response structure"""
        response = Mock()
        response.data = []
        response.error = None
        return response
    
    def test_ensure_daily_calories_table_exists(self, calories_service, mock_supabase_response):
        """Test that table existence check works correctly"""
        # Mock successful table check
        calories_service.supabase.table.return_value.select.return_value.limit.return_value.execute.return_value = mock_supabase_response
        
        result = calories_service.ensure_daily_calories_table()
        
        assert result is True
        calories_service.supabase.table.assert_called_with("daily_calories")
    
    def test_ensure_daily_calories_table_creates_if_not_exists(self, calories_service, mock_supabase_response):
        """Test that table is created if it doesn't exist"""
        # Mock table doesn't exist (raises exception)
        calories_service.supabase.table.return_value.select.return_value.limit.return_value.execute.side_effect = Exception("Table not found")
        
        # Mock successful table creation
        calories_service.supabase.rpc.return_value.execute.return_value = mock_supabase_response
        
        result = calories_service.ensure_daily_calories_table()
        
        assert result is True
        calories_service.supabase.rpc.assert_called()
    
    def test_add_calories_new_record(self, calories_service, mock_supabase_response):
        """Test adding calories when no record exists for today"""
        # Mock table exists
        calories_service.ensure_daily_calories_table = Mock(return_value=True)
        
        # Mock no existing record
        mock_supabase_response.data = []
        calories_service.supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_supabase_response
        
        # Mock successful insert
        insert_response = Mock()
        insert_response.data = [{'id': 'test-id'}]
        calories_service.supabase.table.return_value.insert.return_value.execute.return_value = insert_response
        
        result = calories_service.add_calories_from_analysis("test-user-id", 300.0, 20.0, 10.0, 30.0)
        
        assert result is True
        calories_service.supabase.table.return_value.insert.assert_called_once()
    
    def test_add_calories_update_existing_record(self, calories_service, mock_supabase_response):
        """Test updating calories when record exists for today"""
        # Mock table exists
        calories_service.ensure_daily_calories_table = Mock(return_value=True)
        
        # Mock existing record
        mock_supabase_response.data = [{
            'id': 'existing-id',
            'total_calories': 500.0,
            'total_proteins': 30.0,
            'total_fats': 15.0,
            'total_carbohydrates': 60.0
        }]
        calories_service.supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_supabase_response
        
        # Mock successful update
        update_response = Mock()
        update_response.data = [{'id': 'existing-id'}]
        calories_service.supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = update_response
        
        result = calories_service.add_calories_from_analysis("test-user-id", 200.0, 15.0, 8.0, 25.0)
        
        assert result is True
        calories_service.supabase.table.return_value.update.assert_called_once()
    
    def test_get_daily_summary_with_data(self, calories_service, mock_supabase_response):
        """Test getting daily summary when data exists"""
        # Mock table exists
        calories_service.ensure_daily_calories_table = Mock(return_value=True)
        
        # Mock existing record
        mock_supabase_response.data = [{
            'total_calories': 800.0,
            'total_proteins': 45.0,
            'total_fats': 25.0,
            'total_carbohydrates': 85.0
        }]
        calories_service.supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_supabase_response
        
        result = calories_service.get_daily_summary("test-user-id")
        
        assert result is not None
        assert result['total_calories'] == 800.0
        assert result['total_proteins'] == 45.0
        assert result['total_fats'] == 25.0
        assert result['total_carbohydrates'] == 85.0
    
    def test_get_daily_summary_no_data(self, calories_service, mock_supabase_response):
        """Test getting daily summary when no data exists"""
        # Mock table exists
        calories_service.ensure_daily_calories_table = Mock(return_value=True)
        
        # Mock no existing record
        mock_supabase_response.data = []
        calories_service.supabase.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value = mock_supabase_response
        
        result = calories_service.get_daily_summary("test-user-id")
        
        assert result is not None
        assert result['total_calories'] == 0.0
        assert result['total_proteins'] == 0.0
        assert result['total_fats'] == 0.0
        assert result['total_carbohydrates'] == 0.0
    
    def test_get_user_target_calories_with_profile(self, calories_service, mock_supabase_response):
        """Test getting user target calories when profile exists"""
        # Mock profile with target calories
        mock_supabase_response.data = [{'daily_calories_target': 2500}]
        calories_service.supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_supabase_response
        
        result = calories_service.get_user_target_calories("test-user-id")
        
        assert result == 2500
    
    def test_get_user_target_calories_no_profile(self, calories_service, mock_supabase_response):
        """Test getting user target calories when no profile exists"""
        # Mock no profile data
        mock_supabase_response.data = []
        calories_service.supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_supabase_response
        
        result = calories_service.get_user_target_calories("test-user-id")
        
        assert result == 2000  # Default value
    
    def test_calculate_daily_progress(self, calories_service):
        """Test calculating daily progress"""
        # Mock daily summary
        calories_service.get_daily_summary = Mock(return_value={
            'total_calories': 1200.0,
            'total_proteins': 60.0,
            'total_fats': 40.0,
            'total_carbohydrates': 150.0
        })
        
        # Mock target calories
        calories_service.get_user_target_calories = Mock(return_value=2000)
        
        result = calories_service.calculate_daily_progress("test-user-id")
        
        assert result['eaten_calories'] == 1200.0
        assert result['target_calories'] == 2000
        assert result['remaining_calories'] == 800.0
        assert result['progress_percentage'] == 60.0
    
    def test_calculate_daily_progress_exceeds_target(self, calories_service):
        """Test calculating daily progress when eaten exceeds target"""
        # Mock daily summary exceeding target
        calories_service.get_daily_summary = Mock(return_value={
            'total_calories': 2500.0,
            'total_proteins': 120.0,
            'total_fats': 80.0,
            'total_carbohydrates': 300.0
        })
        
        # Mock target calories
        calories_service.get_user_target_calories = Mock(return_value=2000)
        
        result = calories_service.calculate_daily_progress("test-user-id")
        
        assert result['eaten_calories'] == 2500.0
        assert result['target_calories'] == 2000
        assert result['remaining_calories'] == 0.0
        assert result['progress_percentage'] == 100.0
    
    def test_error_handling_add_calories(self, calories_service):
        """Test error handling when adding calories fails"""
        # Mock table creation failure
        calories_service.ensure_daily_calories_table = Mock(return_value=False)
        
        result = calories_service.add_calories_from_analysis("test-user-id", 300.0)
        
        assert result is False
    
    def test_error_handling_get_daily_summary(self, calories_service):
        """Test error handling when getting daily summary fails"""
        # Mock table creation failure
        calories_service.ensure_daily_calories_table = Mock(return_value=False)
        
        result = calories_service.get_daily_summary("test-user-id")
        
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__]) 