# Payment Configuration - Single source of truth for Stripe
# NOTE: Set to minimum Telegram-accepted amounts for testing (normally 99 and 399 rubles)
PAYMENT_PLANS = {
    "basic": {
        "title": "Basic Plan",
        "description": "20 credits for food analysis",
        "price": 1000,  # 10 RUB in kopecks (minimum Telegram amount for testing, normally 9900)
        "credits": 20,
        "currency": "RUB",
        "recurring": False
    },
    "pro": {
        "title": "Pro Plan", 
        "description": "100 credits for food analysis",
        "price": 5000,  # 50 RUB in kopecks (minimum Telegram amount for testing, normally 39900)
        "credits": 100,
        "currency": "RUB",
        "recurring": True,
        "interval": "month"
    }
}

# Adapt PAYMENT_PLANS for Stripe format
PLANS_STRIPE = {
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
for plan_id, plan in PLANS_STRIPE.items():
    if plan["recurring"] and "interval" in PAYMENT_PLANS[plan_id]:
        plan["interval"] = PAYMENT_PLANS[plan_id]["interval"] 