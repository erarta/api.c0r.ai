"""
Region detection utility for payment system routing
Determines payment provider based on user's language/region:
- CIS countries (language codes) -> YooKassa
- International users -> Stripe + Telegram Stars
"""
from typing import Dict, List, Literal
from loguru import logger

# Коды языков стран СНГ
CIS_LANGUAGE_CODES = {
    'ru',  # Россия
    'kk',  # Казахстан  
    'uz',  # Узбекистан
    'ky',  # Кыргызстан
    'tg',  # Таджикистан
    'tk',  # Туркменистан
    'az',  # Азербайджан
    'hy',  # Армения
    'ka',  # Грузия
    'be',  # Беларусь
    'uk',  # Украина
    'mo',  # Молдова
}

PaymentProvider = Literal['yookassa', 'stripe', 'telegram_stars']

def is_cis_region(language_code: str) -> bool:
    """
    Determine if user is from CIS region based on language code
    
    Args:
        language_code: Telegram language code (e.g., 'ru', 'en', 'de')
        
    Returns:
        True if user is from CIS region, False otherwise
    """
    if not language_code:
        return False
        
    # Normalize language code to lowercase
    lang_code = language_code.lower().strip()
    
    # Extract base language code (e.g., 'ru-RU' -> 'ru')
    base_lang = lang_code.split('-')[0]
    
    is_cis = base_lang in CIS_LANGUAGE_CODES
    
    logger.debug(f"Language code '{language_code}' -> base: '{base_lang}' -> CIS: {is_cis}")
    return is_cis

def get_payment_provider(language_code: str) -> PaymentProvider:
    """
    Get appropriate payment provider for user's region
    
    Args:
        language_code: Telegram language code
        
    Returns:
        'yookassa' for CIS regions, 'stripe' for others
    """
    if is_cis_region(language_code):
        return 'yookassa'
    else:
        return 'stripe'

def get_available_payment_providers(language_code: str) -> List[PaymentProvider]:
    """
    Get list of available payment providers for user's region
    
    Args:
        language_code: Telegram language code
        
    Returns:
        List of available payment providers for the region
    """
    if is_cis_region(language_code):
        # СНГ: Только YooKassa
        return ['yookassa']
    else:
        # Международные пользователи: Stripe + Telegram Stars
        return ['stripe', 'telegram_stars']

def get_primary_currency(language_code: str) -> str:
    """
    Get primary currency for user's region
    
    Args:
        language_code: Telegram language code
        
    Returns:
        Currency code ('RUB' for CIS, 'USD' for international)
    """
    return 'RUB' if is_cis_region(language_code) else 'USD'

def validate_language_code(language_code: str) -> str:
    """
    Validate and normalize language code
    
    Args:
        language_code: Raw language code from Telegram
        
    Returns:
        Normalized language code ('en' or 'ru')
    """
    if not language_code:
        return 'en'
        
    # Normalize and extract base language
    base_lang = language_code.lower().strip().split('-')[0]
    
    # Map to supported languages
    if base_lang in CIS_LANGUAGE_CODES:
        return 'ru'  # Use Russian for all CIS countries
    else:
        return 'en'  # Use English for international users

# Regional configuration for debugging and testing
REGION_CONFIG = {
    'cis': {
        'languages': list(CIS_LANGUAGE_CODES),
        'primary_provider': 'yookassa',
        'currency': 'RUB',
        'fallback_language': 'ru'
    },
    'international': {
        'languages': ['en', 'de', 'fr', 'es', 'it', 'pt', 'nl', 'sv', 'no', 'da', 'fi'],
        'primary_provider': 'stripe',
        'currency': 'USD',
        'fallback_language': 'en'
    }
}



if __name__ == "__main__":
    # Test cases
    test_cases = [
        'ru',      # Russia
        'ru-RU',   # Russia with region
        'en',      # English
        'en-US',   # English US
        'de',      # German
        'kk',      # Kazakh
        'uz',      # Uzbek
        None,      # No language
        '',        # Empty string
        'unknown', # Unknown language
    ]
    
    print("=== Region Detection Test ===")
    for lang in test_cases:
        is_cis = is_cis_region(lang)
        provider = get_payment_provider(lang)
        available = get_available_payment_providers(lang)
        print(f"Language: {lang or 'None':<8} -> CIS: {is_cis}, Provider: {provider}, Available: {available}")
