import os
from yookassa import Payment
from .config import PLANS_YOOKASSA

YOOKASSA_PROVIDER_TOKEN = os.getenv("YOOKASSA_PROVIDER_TOKEN")

async def create_yookassa_invoice(user_id: int, plan_id: str) -> dict:
    plan = PLANS_YOOKASSA.get(plan_id)
    if not plan:
        raise ValueError("Unknown plan_id")
    # Заглушка: здесь будет реальный вызов YooKassa SDK
    # payment = Payment.create({
    #     "amount": {"value": f"{plan['amount']/100:.2f}", "currency": "RUB"},
    #     "confirmation": {"type": "redirect", "return_url": "https://api.c0r.ai/payment/success"},
    #     "capture": True,
    #     "description": plan["description"],
    #     "metadata": {
    #         "user_id": user_id,
    #         "count": plan["count"],
    #         "plan_id": plan_id,
    #         "recurring": plan["recurring"],
    #         "interval": plan.get("interval")
    #     }
    # }, YOOKASSA_PROVIDER_TOKEN)
    # return {"invoice_url": payment.confirmation.confirmation_url, "status": payment.status}
    return {
        "invoice_url": "https://pay.yookassa.ru/stub",
        "status": "created",
        "plan_id": plan_id,
        "count": plan["count"],
        "amount": plan["amount"],
        "recurring": plan["recurring"],
        "interval": plan.get("interval")
    } 