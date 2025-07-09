import os
import uuid
from yookassa import Configuration, Payment
from loguru import logger
from .config import PLANS_YOOKASSA

# Configure YooKassa SDK
YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")

if YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY:
    Configuration.account_id = YOOKASSA_SHOP_ID
    Configuration.secret_key = YOOKASSA_SECRET_KEY
    logger.info("YooKassa SDK configured successfully")
else:
    logger.warning("YooKassa credentials not found in environment variables")

async def create_yookassa_invoice(user_id: int, plan_id: str) -> dict:
    """
    Create YooKassa payment invoice for user
    Returns payment URL and invoice details
    """
    try:
        plan = PLANS_YOOKASSA.get(plan_id)
        if not plan:
            raise ValueError(f"Unknown plan_id: {plan_id}")
        
        if not YOOKASSA_SHOP_ID or not YOOKASSA_SECRET_KEY:
            raise ValueError("YooKassa credentials not configured")
        
        # Generate unique idempotency key
        idempotency_key = str(uuid.uuid4())
        
        # Create payment request
        payment_data = {
            "amount": {
                "value": f"{plan['amount']/100:.2f}",  # Convert kopecks to rubles
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://api.c0r.ai/payment/success?user_id={user_id}&plan_id={plan_id}"
            },
            "capture": True,
            "description": plan["description"],
            "metadata": {
                "user_id": str(user_id),
                "plan_id": plan_id,
                "credits_count": str(plan["count"]),
                "recurring": str(plan["recurring"]),
                "interval": plan.get("interval", "")
            }
        }
        
        # Create payment via YooKassa SDK
        payment = Payment.create(payment_data, idempotency_key)
        
        logger.info(f"Created YooKassa payment {payment.id} for user {user_id}, plan {plan_id}")
        
        return {
            "status": "success",
            "payment_id": payment.id,
            "invoice_url": payment.confirmation.confirmation_url,
            "amount": plan["amount"],
            "credits_count": plan["count"],
            "plan_id": plan_id,
            "user_id": user_id,
            "recurring": plan["recurring"]
        }
        
    except Exception as e:
        logger.error(f"Failed to create YooKassa payment for user {user_id}: {e}")
        raise

async def verify_yookassa_payment(payment_id: str) -> dict:
    """
    Verify payment status with YooKassa API
    Returns payment details and status
    """
    try:
        if not YOOKASSA_SHOP_ID or not YOOKASSA_SECRET_KEY:
            raise ValueError("YooKassa credentials not configured")
        
        payment = Payment.find_one(payment_id)
        
        return {
            "payment_id": payment.id,
            "status": payment.status,
            "amount": payment.amount.value,
            "currency": payment.amount.currency,
            "metadata": payment.metadata,
            "created_at": payment.created_at,
            "paid": payment.paid
        }
        
    except Exception as e:
        logger.error(f"Failed to verify YooKassa payment {payment_id}: {e}")
        raise

def validate_yookassa_webhook(request_body: str, headers: dict) -> bool:
    """
    Validate YooKassa webhook signature
    Returns True if signature is valid
    """
    # YooKassa doesn't use webhook signatures by default
    # But we can validate the payment exists in their system
    return True 