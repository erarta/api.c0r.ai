"""
Payment Plans Configuration - Single Source of Truth
Centralized configuration for all payment plans across all services.
"""
import os
from typing import Dict, Any, Optional

# Environment-based configuration
def get_environment() -> str:
    """Get current environment (production, staging, development)"""
    return os.getenv("ENVIRONMENT", "development").lower()

def is_production() -> bool:
    """Check if running in production environment"""
    return get_environment() == "production"

def is_test_mode() -> bool:
    """Check if running in test mode (for Telegram minimum amounts)"""
    return os.getenv("TEST_MODE", "false").lower() == "true"

# Base payment plans configuration
BASE_PAYMENT_PLANS = {
    "basic": {
        "title": "Basic Plan",
        "description": "20 credits for food analysis",
        "credits": 20,
        "currency": "RUB",
        "recurring": False
    },
    "pro": {
        "title": "Pro Plan", 
        "description": "100 credits for food analysis",
        "credits": 100,
        "currency": "RUB",
        "recurring": True,
        "interval": "month"
    }
}

# Price configuration based on environment
PRICE_CONFIG = {
    "production": {
        "basic": 9900,   # 99 RUB in kopecks
        "pro": 34900,    # 349 RUB in kopecks
    },
    "staging": {
        "basic": 9900,   # Same as production for staging
        "pro": 34900,
    },
    "development": {
        "basic": 1000,   # 10 RUB in kopecks (minimum Telegram amount)
        "pro": 5000,     # 50 RUB in kopecks (minimum Telegram amount)
    },
    "test": {
        "basic": 1000,   # Minimum amounts for testing
        "pro": 5000,
    }
}

def get_payment_plans() -> Dict[str, Dict[str, Any]]:
    """
    Get payment plans with environment-appropriate pricing.
    
    Returns:
        Dict containing payment plans with correct prices for current environment
    """
    env = get_environment()
    
    # Use test prices if TEST_MODE is enabled, regardless of environment
    if is_test_mode():
        env = "test"
    
    # Get prices for current environment
    prices = PRICE_CONFIG.get(env, PRICE_CONFIG["development"])
    
    # Build payment plans with appropriate prices
    payment_plans = {}
    for plan_id, base_plan in BASE_PAYMENT_PLANS.items():
        payment_plans[plan_id] = {
            **base_plan,
            "price": prices[plan_id]
        }
    
    return payment_plans

def get_plan_by_id(plan_id: str) -> Optional[Dict[str, Any]]:
    """
    Get specific payment plan by ID.
    
    Args:
        plan_id: Plan identifier ('basic' or 'pro')
        
    Returns:
        Payment plan dictionary or None if not found
    """
    plans = get_payment_plans()
    return plans.get(plan_id)

def get_plan_price(plan_id: str) -> Optional[int]:
    """
    Get price for specific plan in kopecks.
    
    Args:
        plan_id: Plan identifier ('basic' or 'pro')
        
    Returns:
        Price in kopecks or None if plan not found
    """
    plan = get_plan_by_id(plan_id)
    return plan["price"] if plan else None

def get_plan_credits(plan_id: str) -> Optional[int]:
    """
    Get credits amount for specific plan.
    
    Args:
        plan_id: Plan identifier ('basic' or 'pro')
        
    Returns:
        Credits amount or None if plan not found
    """
    plan = get_plan_by_id(plan_id)
    return plan["credits"] if plan else None

# Export the main configuration
PAYMENT_PLANS = get_payment_plans()

# Backward compatibility - static export for immediate import
# This will be updated when environment changes
_current_plans = get_payment_plans()
BASIC_PLAN = _current_plans["basic"]
PRO_PLAN = _current_plans["pro"]

# Validation
def validate_payment_plans() -> bool:
    """
    Validate payment plans configuration.
    
    Returns:
        True if configuration is valid, False otherwise
    """
    plans = get_payment_plans()
    
    required_fields = ["title", "description", "price", "credits", "currency"]
    
    for plan_id, plan in plans.items():
        # Check required fields
        for field in required_fields:
            if field not in plan:
                print(f"Missing required field '{field}' in plan '{plan_id}'")
                return False
        
        # Validate price is positive
        if plan["price"] <= 0:
            print(f"Invalid price {plan['price']} for plan '{plan_id}'")
            return False
            
        # Validate credits is positive
        if plan["credits"] <= 0:
            print(f"Invalid credits {plan['credits']} for plan '{plan_id}'")
            return False
    
    return True

if __name__ == "__main__":
    # Test the configuration
    print("Current environment:", get_environment())
    print("Is production:", is_production())
    print("Is test mode:", is_test_mode())
    print("\nPayment plans:")
    
    for plan_id, plan in get_payment_plans().items():
        print(f"  {plan_id}: {plan['price']} kopecks ({plan['price']/100} RUB) - {plan['credits']} credits")
    
    print("\nValidation:", "PASSED" if validate_payment_plans() else "FAILED")