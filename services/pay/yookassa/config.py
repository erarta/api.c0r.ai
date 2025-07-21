"""
YooKassa Payment Configuration
Uses centralized payment plans configuration with YooKassa-specific adaptations.
"""
import os
import sys

# Add common directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'common'))

from config.payment_plans import get_payment_plans

# Get payment plans from centralized configuration
PAYMENT_PLANS = get_payment_plans()

# Adapt PAYMENT_PLANS for YooKassa format
PLANS_YOOKASSA = {
    plan_id: {
        "name": plan["title"].replace(" Plan", ""),  # "Basic Plan" -> "Basic"
        "count": plan["credits"],
        "amount": plan["price"],
        "description": plan["description"],
        "recurring": plan["recurring"]
    }
    for plan_id, plan in PAYMENT_PLANS.items()
}

# Add interval for recurring plans
for plan_id, plan in PLANS_YOOKASSA.items():
    if plan["recurring"] and "interval" in PAYMENT_PLANS[plan_id]:
        plan["interval"] = PAYMENT_PLANS[plan_id]["interval"] 