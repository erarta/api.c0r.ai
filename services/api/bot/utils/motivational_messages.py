"""
Utility functions for generating random motivational messages
to avoid repetition and keep the bot engaging.
"""

import random
from typing import Optional
from i18n.i18n import i18n


def get_random_motivational_message(
    base_key: str,
    user_language: str = 'en',
    fallback_to_base: bool = True,
    **format_kwargs
) -> str:
    """
    Get a random motivational message from variants or fallback to base message.
    
    Args:
        base_key: The base translation key (e.g., 'profile_setup_step')
        user_language: User's language preference
        fallback_to_base: If True, falls back to base key if variants don't exist
        **format_kwargs: Additional formatting arguments
    
    Returns:
        Random motivational message string
    """
    variants_key = f"{base_key}_variants"
    
    # Import the translations directly to get the variants
    if user_language == 'ru':
        from i18n.ru.profile import TRANSLATIONS
    else:
        from i18n.en.profile import TRANSLATIONS
    
    # Try to get variants first
    variants = TRANSLATIONS.get(variants_key)
    
    # If variants exist and it's a list, pick random one
    if variants and isinstance(variants, list) and len(variants) > 0:
        selected_message = random.choice(variants)
        return selected_message.format(**format_kwargs) if format_kwargs else selected_message
    
    # Fallback to base message if variants don't exist
    if fallback_to_base:
        base_message = TRANSLATIONS.get(base_key) or i18n.get_text(base_key, user_language)
        return base_message.format(**format_kwargs) if format_kwargs else base_message
    
    # Return empty string if no fallback
    return ""


def get_profile_step_message(user_language: str = 'en', step: int = 1, total: int = 8) -> str:
    """
    Get a random step progress message for profile setup.
    
    Args:
        user_language: User's language preference  
        step: Current step number
        total: Total number of steps
    
    Returns:
        Random step progress message
    """
    return get_random_motivational_message(
        'profile_setup_step',
        user_language,
        step=step,
        total=total
    )


def get_profile_tip_message(tip_type: str, user_language: str = 'en') -> str:
    """
    Get a random tip message for profile setup.
    
    Args:
        tip_type: Type of tip ('important', 'restart', 'dietary', 'allergies')
        user_language: User's language preference
    
    Returns:
        Random tip message
    """
    tip_key = f"profile_setup_{tip_type}"
    return get_random_motivational_message(tip_key, user_language)


# Convenience functions for specific use cases
def get_random_important_tip(user_language: str = 'en') -> str:
    """Get random 'important' tip message."""
    return get_profile_tip_message('important', user_language)


def get_random_restart_tip(user_language: str = 'en') -> str:
    """Get random 'restart' tip message."""
    return get_profile_tip_message('restart', user_language)


def get_random_dietary_tip(user_language: str = 'en') -> str:
    """Get random dietary preferences tip message."""
    return get_profile_tip_message('dietary', user_language)


def get_random_allergies_tip(user_language: str = 'en') -> str:
    """Get random allergies tip message."""
    return get_profile_tip_message('allergies', user_language) 