from .config import PLANS_STRIPE

async def create_stripe_invoice(user_id: int, plan_id: str) -> dict:
    plan = PLANS_STRIPE.get(plan_id)
    if not plan:
        raise ValueError("Unknown plan_id")
    # TODO: Реальная интеграция со Stripe API
    return {
        "invoice_url": "https://checkout.stripe.com/pay/stub",
        "status": "created",
        "plan_id": plan_id,
        "count": plan["count"],
        "amount": plan["amount"],
        "recurring": plan["recurring"],
        "interval": plan.get("interval")
    } 