"""
Database module for c0r.AI project
Provides organized access to Supabase operations
"""

from .client import supabase
from .users import (
    get_or_create_user,
    get_user_by_telegram_id,
    update_user_language,
    update_user_language
)
from .credits import (
    add_credits,
    decrement_credits
)
from .profiles import (
    get_user_profile,
    get_user_with_profile,
    create_user_profile,
    update_user_profile,
    validate_profile_completeness,
    calculate_daily_calories,
    create_or_update_profile,
    get_daily_calories_consumed
)
from .logs import (
    log_user_action,
    log_analysis
)
from .payments import (
    add_payment,
    get_user_total_paid
)
from .favorites import (
    save_favorite_food,
    list_favorites,
    get_favorite_by_id,
    delete_favorite,
)
from .recipes import (
    save_recipe,
    list_recipes,
    get_recipe_by_id,
    delete_recipe,
)

__all__ = [
    # Client
    'supabase',
    
    # Users
    'get_or_create_user',
    'get_user_by_telegram_id', 
    'decrement_credits',
    'add_credits',
    'update_user_language',
    'update_user_language',
    
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
    'get_user_total_paid',
    
    # Favorites
    'save_favorite_food',
    'list_favorites',
    'get_favorite_by_id',
    'delete_favorite',
    
    # Recipes
    'save_recipe',
    'list_recipes',
    'get_recipe_by_id',
    'delete_recipe'
]