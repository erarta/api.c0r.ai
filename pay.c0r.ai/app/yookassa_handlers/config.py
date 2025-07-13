# Payment Configuration - Single source of truth for YooKassa
# NOTE: Temporarily set to 1 and 5 rubles for testing (normally 99 and 399 rubles)
PAYMENT_PLANS = {
    "basic": {
        "title": "Basic Plan",
        "description": "20 credits for food analysis",
        "price": 100,  # 1 RUB in kopecks (temporarily for testing, normally 9900)
        "credits": 20,
        "currency": "RUB",
        "recurring": False
    },
    "pro": {
        "title": "Pro Plan", 
        "description": "100 credits for food analysis",
        "price": 500,  # 5 RUB in kopecks (temporarily for testing, normally 39900)
        "credits": 100,
        "currency": "RUB",
        "recurring": True,
        "interval": "month"
    }
}

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