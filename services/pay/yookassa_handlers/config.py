"""
YooKassa payment configuration
"""
import sys
import os

# Add common directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'common'))

from common.config.payment_plans import PAYMENT_PLANS

# YooKassa specific configuration
PLANS_YOOKASSA = PAYMENT_PLANS

# YooKassa credentials
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")