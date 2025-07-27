"""
Test centralized payment plans configuration
"""
import pytest
import sys
import os
import unittest.mock

# Add common directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'common')))

from config.payment_plans import (
    get_payment_plans, 
    get_plan_by_id, 
    get_plan_price, 
    get_plan_credits,
    validate_payment_plans,
    is_production,
    is_test_mode,
    get_environment
)


class TestPaymentPlansConfig:
    """Test centralized payment plans configuration"""
    
    def test_get_payment_plans_development(self):
        """Test payment plans in development environment"""
        with unittest.mock.patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            plans = get_payment_plans()
            
            assert 'basic' in plans
            assert 'pro' in plans
            
            # Development prices (minimum Telegram amounts)
            assert plans['basic']['price'] == 1000  # 10 RUB
            assert plans['pro']['price'] == 5000    # 50 RUB
            
            # Credits should be consistent
            assert plans['basic']['credits'] == 20
            assert plans['pro']['credits'] == 100
    
    def test_get_payment_plans_production(self):
        """Test payment plans in production environment"""
        with unittest.mock.patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
            plans = get_payment_plans()
            
            assert 'basic' in plans
            assert 'pro' in plans
            
            # Production prices
            assert plans['basic']['price'] == 9900   # 99 RUB
            assert plans['pro']['price'] == 34900    # 349 RUB
            
            # Credits should be consistent
            assert plans['basic']['credits'] == 20
            assert plans['pro']['credits'] == 100
    
    def test_test_mode_override(self):
        """Test that TEST_MODE overrides environment pricing"""
        with unittest.mock.patch.dict(os.environ, {
            'ENVIRONMENT': 'production',
            'TEST_MODE': 'true'
        }):
            plans = get_payment_plans()
            
            # Should use test prices even in production
            assert plans['basic']['price'] == 1000  # 10 RUB
            assert plans['pro']['price'] == 5000    # 50 RUB
    
    def test_get_plan_by_id(self):
        """Test getting specific plan by ID"""
        with unittest.mock.patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            basic_plan = get_plan_by_id('basic')
            pro_plan = get_plan_by_id('pro')
            invalid_plan = get_plan_by_id('invalid')
            
            assert basic_plan is not None
            assert basic_plan['title'] == 'Basic Plan'
            assert basic_plan['credits'] == 20
            
            assert pro_plan is not None
            assert pro_plan['title'] == 'Pro Plan'
            assert pro_plan['credits'] == 100
            
            assert invalid_plan is None
    
    def test_get_plan_price(self):
        """Test getting plan price"""
        with unittest.mock.patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            basic_price = get_plan_price('basic')
            pro_price = get_plan_price('pro')
            invalid_price = get_plan_price('invalid')
            
            assert basic_price == 1000
            assert pro_price == 5000
            assert invalid_price is None
    
    def test_get_plan_credits(self):
        """Test getting plan credits"""
        basic_credits = get_plan_credits('basic')
        pro_credits = get_plan_credits('pro')
        invalid_credits = get_plan_credits('invalid')
        
        assert basic_credits == 20
        assert pro_credits == 100
        assert invalid_credits is None
    
    def test_environment_detection(self):
        """Test environment detection functions"""
        with unittest.mock.patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
            assert get_environment() == 'production'
            assert is_production() is True
        
        with unittest.mock.patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            assert get_environment() == 'development'
            assert is_production() is False
        
        with unittest.mock.patch.dict(os.environ, {}):
            assert get_environment() == 'development'  # Default
            assert is_production() is False
    
    def test_test_mode_detection(self):
        """Test test mode detection"""
        with unittest.mock.patch.dict(os.environ, {'TEST_MODE': 'true'}):
            assert is_test_mode() is True
        
        with unittest.mock.patch.dict(os.environ, {'TEST_MODE': 'false'}):
            assert is_test_mode() is False
        
        with unittest.mock.patch.dict(os.environ, {}):
            assert is_test_mode() is False  # Default
    
    def test_validate_payment_plans(self):
        """Test payment plans validation"""
        with unittest.mock.patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            assert validate_payment_plans() is True
    
    def test_plan_structure(self):
        """Test that all plans have required fields"""
        plans = get_payment_plans()
        required_fields = ['title', 'description', 'price', 'credits', 'currency']
        
        for plan_id, plan in plans.items():
            for field in required_fields:
                assert field in plan, f"Missing field '{field}' in plan '{plan_id}'"
            
            # Validate data types
            assert isinstance(plan['price'], int)
            assert isinstance(plan['credits'], int)
            assert isinstance(plan['title'], str)
            assert isinstance(plan['description'], str)
            assert isinstance(plan['currency'], str)
            
            # Validate positive values
            assert plan['price'] > 0
            assert plan['credits'] > 0
    
    def test_currency_consistency(self):
        """Test that all plans use RUB currency"""
        plans = get_payment_plans()
        
        for plan_id, plan in plans.items():
            assert plan['currency'] == 'RUB', f"Plan '{plan_id}' should use RUB currency"
    
    def test_recurring_plan_has_interval(self):
        """Test that recurring plans have interval field"""
        plans = get_payment_plans()
        
        for plan_id, plan in plans.items():
            if plan.get('recurring', False):
                assert 'interval' in plan, f"Recurring plan '{plan_id}' should have interval"
                assert plan['interval'] in ['month', 'year'], f"Invalid interval for plan '{plan_id}'"


if __name__ == '__main__':
    pytest.main([__file__])