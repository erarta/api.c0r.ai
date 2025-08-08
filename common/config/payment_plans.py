"""
Payment Plans Configuration - Single Source of Truth
Centralized configuration for all payment plans across all services.
Now supports regional payment providers and currencies.
"""
import os
import sys
from typing import Dict, Any, Optional, Literal, List

# Add project root to path for imports
project_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, project_root)

try:
    from i18n.i18n import I18nManager
    from common.utils.region_detector import is_cis_region, get_payment_provider, get_primary_currency
    # Create i18n instance
    i18n = I18nManager()
except ImportError as e:
    print(f"Warning: Import error in payment_plans.py: {e}")
    # Fallback for standalone testing
    class MockI18nManager:
        def get_text(self, key: str, language: str = "en", **kwargs) -> str:
            # Mock translations for testing
            mock_translations = {
                "plan_basic_title": "Basic Plan",
                "plan_basic_description": "20 credits for food analysis",
                "plan_pro_title": "Pro Plan", 
                "plan_pro_description": "100 credits for food analysis"
            }
            return mock_translations.get(key, f"[{key}]")
    
    i18n = MockI18nManager()
    
    # Mock region detector functions for standalone testing
    def is_cis_region(language_code: str) -> bool:
        cis_codes = {'ru', 'kk', 'uz', 'ky', 'tg', 'tk', 'az', 'hy', 'ka', 'be', 'uk', 'mo'}
        return language_code.lower().split('-')[0] in cis_codes
    
    def get_payment_provider(language_code: str) -> str:
        return 'yookassa' if is_cis_region(language_code) else 'stripe'
    
    def get_primary_currency(language_code: str) -> str:
        return 'RUB' if is_cis_region(language_code) else 'USD'

PaymentProvider = Literal['yookassa', 'stripe', 'telegram_stars']

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

def get_payment_plans_for_language(language: str = "en") -> Dict[str, Dict[str, Any]]:
    """
    Get payment plans with translated titles and descriptions for specific language.
    DEPRECATED: Use get_payment_plans_for_region() instead.
    
    Args:
        language: Language code ('en' or 'ru')
        
    Returns:
        Dict containing payment plans with translated content
    """
    # For backward compatibility, assume CIS region if Russian
    return get_payment_plans_for_region(language, force_legacy=True)

def get_payment_plans_for_region(language: str = "en", provider: Optional[PaymentProvider] = None, force_legacy: bool = False) -> Dict[str, Dict[str, Any]]:
    """
    Get payment plans based on user's region and payment provider
    
    Args:
        language: User's language code
        provider: Specific payment provider to use (None = auto-detect from region)
        force_legacy: Use legacy single-provider logic for backward compatibility
        
    Returns:
        Dict containing payment plans with appropriate provider and currency
    """
    # Determine payment provider
    if provider is None:
        provider = get_payment_provider(language)
        
    # Get primary currency for region
    currency = get_primary_currency(language)
    
    # Special handling for legacy compatibility
    if force_legacy and is_cis_region(language):
        provider = 'yookassa'
        currency = 'RUB'
    
    # Get base plan configuration
    base_plans = get_base_plans(language, currency, provider)
    
    # Get prices for current environment and provider
    env = get_environment()
    if is_test_mode():
        env = "test"
    
    prices = get_price_config_for_provider(provider, env)
    
    # Build payment plans with appropriate prices
    payment_plans = {}
    for plan_id, base_plan in base_plans.items():
        payment_plans[plan_id] = {
            **base_plan,
            "price": prices.get(plan_id, 0),  # Fallback to 0 if price not found
            "provider": provider
        }
    
    return payment_plans

def get_base_plans(language: str, currency: str, provider: PaymentProvider) -> Dict[str, Dict[str, Any]]:
    """
    Get base plan configuration for specific language, currency and provider
    
    Args:
        language: User's language code
        currency: Currency code ('RUB', 'USD', etc.)
        provider: Payment provider
        
    Returns:
        Base plan configuration
    """
    plans = {
        "basic": {
            "title": i18n.get_text("plan_basic_title", language),
            "description": i18n.get_text("plan_basic_description", language),
            "credits": 20,
            "currency": currency,
            "recurring": False,
            "provider": provider
        },
        "pro": {
            "title": i18n.get_text("plan_pro_title", language),
            "description": i18n.get_text("plan_pro_description", language),
            "credits": 100,
            "currency": currency,
            "recurring": True,
            "interval": "month",
            "provider": provider
        }
    }
    
    # Special handling for Telegram Stars
    if provider == 'telegram_stars':
        # Telegram Stars pricing is different
        plans["basic"]["credits"] = 25  # Slightly more credits for Stars
        plans["pro"]["credits"] = 120
        plans["basic"]["currency"] = "XTR"  # Telegram Stars currency
        plans["pro"]["currency"] = "XTR"
    
    return plans

# Base payment plans configuration (for backward compatibility)
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

# Price configuration based on environment and payment provider
PRICE_CONFIG = {
    "yookassa": {
        "production": {
            "basic": 19900,   # 199 RUB in kopecks
            "pro": 34900,     # 349 RUB in kopecks
        },
        "staging": {
            "basic": 19900,   # Same as production for staging
            "pro": 34900,
        },
        "development": {
            "basic": 19900,   # Use production prices in development too
            "pro": 34900,
        },
        "test": {
            "basic": 10000,   # 100 RUB in kopecks (minimum for Telegram test payments)
            "pro": 50000,     # 500 RUB in kopecks
        }
    },
    "stripe": {
        "production": {
            "basic": 199,     # $1.99 in cents
            "pro": 799,       # $7.99 in cents
        },
        "staging": {
            "basic": 199,     # Same as production for staging
            "pro": 799,
        },
        "development": {
            "basic": 199,     # Use production prices in development too
            "pro": 799,
        },
        "test": {
            "basic": 50,      # $0.50 in cents (minimum for testing)
            "pro": 100,       # $1.00 in cents
        }
    },
    "telegram_stars": {
        "production": {
            "basic": 100,     # 100 Telegram Stars
            "pro": 400,       # 400 Telegram Stars
        },
        "staging": {
            "basic": 100,     # Same as production for staging
            "pro": 400,
        },
        "development": {
            "basic": 100,     # Use production prices in development too
            "pro": 400,
        },
        "test": {
            "basic": 1,       # 1 Telegram Star (minimum for testing)
            "pro": 5,         # 5 Telegram Stars
        }
    }
}

def get_price_config_for_provider(provider: PaymentProvider, environment: str) -> Dict[str, int]:
    """
    Get price configuration for specific provider and environment
    
    Args:
        provider: Payment provider
        environment: Current environment
        
    Returns:
        Price configuration dictionary
    """
    provider_config = PRICE_CONFIG.get(provider, {})
    return provider_config.get(environment, provider_config.get("production", {}))

def get_payment_plans() -> Dict[str, Dict[str, Any]]:
    """
    Get payment plans with environment-appropriate pricing.
    Defaults to English language for backward compatibility.
    
    Returns:
        Dict containing payment plans with correct prices for current environment
    """
    return get_payment_plans_for_language("en")

def get_payment_plans_for_user_language(user_language: str = "en") -> Dict[str, Dict[str, Any]]:
    """
    Get payment plans with user's language.
    DEPRECATED: Use get_payment_plans_for_region() instead.
    
    Args:
        user_language: User's language preference
        
    Returns:
        Dict containing payment plans with translated content
    """
    return get_payment_plans_for_region(user_language)

def get_plan_by_id(plan_id: str, language: str = "en", provider: Optional[PaymentProvider] = None) -> Optional[Dict[str, Any]]:
    """
    Get specific payment plan by ID with language and provider support.
    
    Args:
        plan_id: Plan identifier ('basic' or 'pro')
        language: Language code ('en' or 'ru')
        provider: Payment provider (None = auto-detect from region)
        
    Returns:
        Payment plan dictionary or None if not found
    """
    plans = get_payment_plans_for_region(language, provider)
    return plans.get(plan_id)

def get_plan_price(plan_id: str, language: str = "en", provider: Optional[PaymentProvider] = None) -> Optional[int]:
    """
    Get price for specific plan.
    
    Args:
        plan_id: Plan identifier ('basic' or 'pro')
        language: Language code for region detection
        provider: Payment provider (None = auto-detect from region)
        
    Returns:
        Price in provider's currency units or None if plan not found
    """
    plan = get_plan_by_id(plan_id, language, provider)
    return plan["price"] if plan else None

def get_plan_credits(plan_id: str, language: str = "en", provider: Optional[PaymentProvider] = None) -> Optional[int]:
    """
    Get credits amount for specific plan.
    
    Args:
        plan_id: Plan identifier ('basic' or 'pro')
        language: Language code for region detection  
        provider: Payment provider (None = auto-detect from region)
        
    Returns:
        Credits amount or None if plan not found
    """
    plan = get_plan_by_id(plan_id, language, provider)
    return plan["credits"] if plan else None

def get_available_providers_for_language(language: str) -> List[PaymentProvider]:
    """
    Get list of available payment providers for user's language/region
    
    Args:
        language: User's language code
        
    Returns:
        List of available payment providers
    """
    try:
        from common.utils.region_detector import get_available_payment_providers
        return get_available_payment_providers(language)
    except ImportError:
        # Fallback for standalone testing
        if is_cis_region(language):
            return ['yookassa']
        else:
            return ['stripe', 'telegram_stars']

def get_all_payment_options_for_language(language: str) -> Dict[PaymentProvider, Dict[str, Dict[str, Any]]]:
    """
    Get all available payment options for user's language/region
    
    Args:
        language: User's language code
        
    Returns:
        Dictionary with payment providers as keys and their plans as values
    """
    available_providers = get_available_providers_for_language(language)
    all_options = {}
    
    for provider in available_providers:
        all_options[provider] = get_payment_plans_for_region(language, provider)
    
    return all_options

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
    print("=== Payment Plans Configuration Test ===")
    print("Current environment:", get_environment())
    print("Is production:", is_production())
    print("Is test mode:", is_test_mode())
    
    # Test different language codes
    test_languages = ['ru', 'en', 'kk', 'de', 'fr']
    
    for lang in test_languages:
        print(f"\n--- Language: {lang} ---")
        
        # Show region info
        print(f"Is CIS region: {is_cis_region(lang)}")
        print(f"Primary provider: {get_payment_provider(lang)}")
        print(f"Primary currency: {get_primary_currency(lang)}")
        
        # Show all available payment options
        all_options = get_all_payment_options_for_language(lang)
        for provider, plans in all_options.items():
            print(f"\n{provider.upper()} plans:")
            for plan_id, plan in plans.items():
                price_display = f"{plan['price']}"
                if plan['currency'] == 'RUB':
                    price_display += f" kopecks ({plan['price']/100} RUB)"
                elif plan['currency'] == 'USD':
                    price_display += f" cents (${plan['price']/100})"
                elif plan['currency'] == 'XTR':
                    price_display += f" Stars"
                    
                print(f"  {plan_id}: {price_display} - {plan['credits']} credits")
    
    print("\nValidation:", "PASSED" if validate_payment_plans() else "FAILED")