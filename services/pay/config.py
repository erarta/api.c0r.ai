"""
Payment Service Configuration
All payment plans are now centralized in common/config/payment_plans.py
Provider-specific configurations import from the centralized source.
"""
import os
import sys

# Add common directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'common'))

from config.payment_plans import get_payment_plans, PAYMENT_PLANS

# Re-export for backward compatibility
PLANS = PAYMENT_PLANS