"""
Legacy compatibility layer for supabase_client.py
This file maintains backward compatibility while the codebase migrates to the new modular structure.

DEPRECATED: This file will be removed in a future version.
Please update your imports to use the new modular structure:

OLD: from common.supabase_client import get_user_by_telegram_id
NEW: from common.db.users import get_user_by_telegram_id

OR: from common.db import get_user_by_telegram_id
"""

import warnings
from .db import *

# Issue deprecation warning
warnings.warn(
    "supabase_client.py is deprecated. Please use the new modular structure in common.db",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backward compatibility
__all__ = [
    # Client
    'supabase',
    
    # Users
    'get_or_create_user',
    'get_user_by_telegram_id', 
    'decrement_credits',
    'add_credits',
    'update_user_language',
    'update_user_country_and_phone',
    
    # Profiles
    'get_user_profile',
    'get_user_with_profile',
    'create_user_profile',
    'update_user_profile',
    'validate_profile_completeness',
    'calculate_daily_calories',
    'create_or_update_profile',
    'get_daily_calories_consumed',
    
    # Logs
    'log_user_action',
    'log_analysis',
    
    # Payments
    'add_payment',
    'get_user_total_paid'
]