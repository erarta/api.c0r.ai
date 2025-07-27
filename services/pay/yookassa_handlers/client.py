"""
YooKassa payment client implementation
"""
import os
import uuid
from yookassa import Configuration, Payment
from loguru import logger
from .config import PLANS_YOOKASSA, YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY

# Configure YooKassa
if YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY:
    Configuration.account_id = YOOKASSA_SHOP_ID
    Configuration.secret_key = YOOKASSA_SECRET_KEY
    logger.info("YooKassa configuration initialized")
else:
    logger.warning("YooKassa credentials not configured")

async def create_yookassa_invoice(user_id: int, plan_id: str = "basic") -> dict:
    """
    Create YooKassa payment invoice
    
    Args:
        user_id: Telegram user ID
        plan_id: Payment plan ID
        
    Returns:
        dict: Payment invoice data with confirmation URL
        
    Raises:
        ValueError: If plan not found or invalid parameters
        Exception: If payment creation fails
    """
    if not YOOKASSA_SHOP_ID or not YOOKASSA_SECRET_KEY:
        raise Exception("YooKassa credentials not configured")
    
    # Get plan details
    plan = PLANS_YOOKASSA.get(plan_id)
    if not plan:
        raise ValueError(f"Payment plan '{plan_id}' not found")
    
    try:
        # Create payment
        payment = Payment.create({
            "amount": {
                "value": str(plan["price"]),
                "currency": plan["currency"]
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://pay.c0r.ai/payment/success?user_id={user_id}&plan_id={plan_id}"
            },
            "capture": True,
            "description": f"c0r.AI - {plan['name']} ({plan['count']} credits)",
            "metadata": {
                "user_id": str(user_id),
                "plan_id": plan_id,
                "credits_count": str(plan["count"])
            }
        }, uuid.uuid4())
        
        logger.info(f"Created YooKassa payment {payment.id} for user {user_id}, plan {plan_id}")
        
        return {
            "payment_id": payment.id,
            "payment_url": payment.confirmation.confirmation_url,
            "amount": plan["price"],
            "currency": plan["currency"],
            "description": f"{plan['name']} ({plan['count']} credits)",
            "status": payment.status
        }
        
    except Exception as e:
        logger.error(f"Failed to create YooKassa payment for user {user_id}: {e}")
        raise Exception(f"Payment creation failed: {str(e)}")

async def verify_yookassa_payment(payment_id: str) -> dict:
    """
    Verify YooKassa payment status
    
    Args:
        payment_id: YooKassa payment ID
        
    Returns:
        dict: Payment verification result
    """
    try:
        payment = Payment.find_one(payment_id)
        
        return {
            "payment_id": payment.id,
            "status": payment.status,
            "amount": payment.amount.value if payment.amount else None,
            "currency": payment.amount.currency if payment.amount else None,
            "metadata": payment.metadata or {}
        }
        
    except Exception as e:
        logger.error(f"Failed to verify YooKassa payment {payment_id}: {e}")
        raise Exception(f"Payment verification failed: {str(e)}")

def validate_yookassa_webhook(body: str, headers: dict) -> bool:
    """
    Validate YooKassa webhook signature
    
    Args:
        body: Request body
        headers: Request headers
        
    Returns:
        bool: True if webhook is valid
    """
    # For now, basic validation - in production should verify signature
    try:
        # Check if required headers are present
        content_type = headers.get("content-type", "")
        if "application/json" not in content_type.lower():
            return False
        
        # Basic body validation
        if not body or len(body) < 10:
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Webhook validation error: {e}")
        return False