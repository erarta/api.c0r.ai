"""
Telegram Payments handler for c0r.ai bot
Handles native Telegram payments without leaving the app
"""
import os
from aiogram import types
from loguru import logger
from common.supabase_client import get_or_create_user, add_credits

# Environment variables
YOOKASSA_PROVIDER_TOKEN = os.getenv("YOOKASSA_PROVIDER_TOKEN")

# Payment plans configuration
PAYMENT_PLANS = {
    "basic": {
        "title": "Basic Plan",
        "description": "20 credits for food analysis",
        "price": 9900,  # 99 RUB in kopecks
        "credits": 20,
        "currency": "RUB"
    },
    "pro": {
        "title": "Pro Plan", 
        "description": "100 credits for food analysis",
        "price": 39900,  # 399 RUB in kopecks
        "credits": 100,
        "currency": "RUB"
    }
}

async def create_invoice_message(message: types.Message, plan_id: str = "basic"):
    """
    Create and send Telegram invoice message
    """
    try:
        if not YOOKASSA_PROVIDER_TOKEN:
            await message.answer("❌ Payment system is not configured. Please contact support.")
            return

        plan = PAYMENT_PLANS.get(plan_id)
        if not plan:
            await message.answer("❌ Invalid payment plan selected.")
            return

        # Create invoice
        await message.answer_invoice(
            title=plan["title"],
            description=plan["description"],
            payload=f"credits_{plan_id}_{message.from_user.id}",
            provider_token=YOOKASSA_PROVIDER_TOKEN,
            currency=plan["currency"],
            prices=[
                types.LabeledPrice(
                    label=f"{plan['credits']} credits",
                    amount=plan["price"]
                )
            ],
            start_parameter=f"buy_{plan_id}",
            photo_url="https://via.placeholder.com/512x512/4CAF50/FFFFFF?text=c0r.ai",
            photo_width=512,
            photo_height=512,
            need_email=False,
            need_phone_number=False,
            need_shipping_address=False,
            is_flexible=False
        )
        
        logger.info(f"Created invoice for user {message.from_user.id}, plan {plan_id}")
        
    except Exception as e:
        logger.error(f"Failed to create invoice: {e}")
        await message.answer("❌ Failed to create payment. Please try again later.")

async def handle_buy_callback(callback: types.CallbackQuery):
    """
    Handle callback from buy buttons
    """
    try:
        # Extract plan_id from callback data
        plan_id = callback.data.split("_")[1]  # "buy_basic" -> "basic"
        
        # Answer callback to remove loading state
        await callback.answer()
        
        # Create invoice message
        await create_invoice_message(callback.message, plan_id)
        
    except Exception as e:
        logger.error(f"Failed to handle buy callback: {e}")
        await callback.answer("❌ Failed to create payment. Please try again later.")

async def handle_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    """
    Handle pre-checkout query - validate payment before processing
    """
    try:
        # Parse payload to get plan and user info
        payload = pre_checkout_query.invoice_payload
        if not payload.startswith("credits_"):
            await pre_checkout_query.answer(ok=False, error_message="Invalid payment payload")
            return

        # Extract plan_id and user_id from payload
        parts = payload.split("_")
        if len(parts) != 3:
            await pre_checkout_query.answer(ok=False, error_message="Invalid payment format")
            return

        plan_id = parts[1]
        user_id = int(parts[2])
        
        # Validate plan exists
        plan = PAYMENT_PLANS.get(plan_id)
        if not plan:
            await pre_checkout_query.answer(ok=False, error_message="Invalid payment plan")
            return

        # Validate user exists
        user = await get_or_create_user(user_id)
        if not user:
            await pre_checkout_query.answer(ok=False, error_message="User not found")
            return

        # Validate amount
        if pre_checkout_query.total_amount != plan["price"]:
            await pre_checkout_query.answer(ok=False, error_message="Invalid payment amount")
            return

        # All validations passed
        await pre_checkout_query.answer(ok=True)
        logger.info(f"Pre-checkout approved for user {user_id}, plan {plan_id}")
        
    except Exception as e:
        logger.error(f"Pre-checkout validation failed: {e}")
        await pre_checkout_query.answer(ok=False, error_message="Payment validation failed")

async def handle_successful_payment(message: types.Message):
    """
    Handle successful payment - add credits to user account
    """
    try:
        payment = message.successful_payment
        payload = payment.invoice_payload
        
        # Parse payload to get plan and user info
        if not payload.startswith("credits_"):
            logger.error(f"Invalid payment payload: {payload}")
            return

        parts = payload.split("_")
        if len(parts) != 3:
            logger.error(f"Invalid payment format: {payload}")
            return

        plan_id = parts[1]
        user_id = int(parts[2])
        
        # Get plan details
        plan = PAYMENT_PLANS.get(plan_id)
        if not plan:
            logger.error(f"Invalid plan in payment: {plan_id}")
            return

        # Add credits to user account
        updated_user = await add_credits(user_id, plan["credits"])
        
        # Send confirmation message
        await message.answer(
            f"✅ **Payment Successful!**\n\n"
            f"💳 **Plan**: {plan['title']}\n"
            f"⚡ **Credits Added**: {plan['credits']}\n"
            f"💰 **Amount Paid**: {payment.total_amount/100:.2f} {payment.currency}\n"
            f"🔋 **Total Credits**: {updated_user['credits_remaining']}\n\n"
            f"You can now continue analyzing your food photos!",
            parse_mode="Markdown"
        )
        
        logger.info(f"Payment processed successfully for user {user_id}: {plan['credits']} credits added")
        
    except Exception as e:
        logger.error(f"Failed to process successful payment: {e}")
        await message.answer("❌ Payment was successful but there was an error adding credits. Please contact support.") 