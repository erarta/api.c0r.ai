PLANS_YOOKASSA = {
    "basic": {
        "name": "Basic",
        "count": 20,
        "amount": 9900,  # 99 RUB, one-time purchase
        "description": "20 credits for food analysis",
        "recurring": False
    },
    "pro": {
        "name": "Pro",
        "count": 100,
        "amount": 39900,  # 399 RUB
        "description": "100 credits per month (subscription)",
        "recurring": True,
        "interval": "month"
    }
}
# Only YooKassa plans. Do not add Stripe or other providers here. 