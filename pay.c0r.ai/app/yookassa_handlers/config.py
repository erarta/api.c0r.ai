import sys
import os

# Add the API config path
api_config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'api.c0r.ai', 'app')
sys.path.insert(0, api_config_path)

# Import from the API config module
from config import PAYMENT_PLANS

# Remove the path to avoid conflicts
sys.path.pop(0)

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