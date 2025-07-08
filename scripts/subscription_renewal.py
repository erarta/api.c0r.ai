import os
from datetime import datetime, timedelta
# from common.supabase_client import get_all_subscribers, add_payment
# from pay.c0r.ai.app.stripe_client import create_stripe_invoice
# from pay.c0r.ai.app.yookassa_client import create_yookassa_invoice

# Заглушка: пример логики автосписания
async def renew_subscriptions():
    # subscribers = await get_all_subscribers()
    subscribers = [
        {"telegram_id": 123, "plan_id": "pro", "last_payment": datetime.now() - timedelta(days=31)},
        {"telegram_id": 456, "plan_id": "pro_stripe", "last_payment": datetime.now() - timedelta(days=29)}
    ]
    for sub in subscribers:
        days_since = (datetime.now() - sub["last_payment"]).days
        if days_since >= 30:
            print(f"[AUTO-RENEW] User {sub['telegram_id']} plan {sub['plan_id']} — инициировать новый платёж!")
            # await create_yookassa_invoice(sub["telegram_id"], sub["plan_id"])
            # await create_stripe_invoice(sub["telegram_id"], sub["plan_id"])
        else:
            print(f"[OK] User {sub['telegram_id']} plan {sub['plan_id']} — подписка активна ({days_since} дней)")

if __name__ == "__main__":
    import asyncio
    asyncio.run(renew_subscriptions()) 