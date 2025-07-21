"""
Supabase Client - Modular Database Operations
This file now imports from the new modular structure for better organization.

For new code, please import directly from the specific modules:
- from common.db.users import get_user_by_telegram_id
- from common.db.profiles import get_user_profile
- from common.db.logs import log_user_action
- from common.db.payments import add_payment

Or use the unified import:
- from common.db import get_user_by_telegram_id, get_user_profile, etc.
"""

# Import everything from the new modular structure
from .db import *

# Maintain backward compatibility
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