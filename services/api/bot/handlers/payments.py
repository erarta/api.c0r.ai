"""
Enhanced Telegram Payments handler for c0r.ai bot
Supports multiple payment providers: YooKassa, Stripe, Telegram Stars
"""
import os
import sys
from aiogram import types
from loguru import logger
from common.supabase_client import get_or_create_user, add_credits, add_payment, log_user_action
from .keyboards import create_main_menu_keyboard, create_payment_success_keyboard
from services.api.bot.config import PAYMENT_PLANS
import traceback
import json
from i18n.i18n import i18n

# Add project root for imports
project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
sys.path.insert(0, project_root)

from common.config.payment_plans import (
    get_payment_plans_for_user_language, 
    get_all_payment_options_for_language,
    get_payment_plans_for_region
)
from common.utils.region_detector import (
    get_payment_provider, 
    get_available_payment_providers, 
    is_cis_region
)

# Try to import Stripe client
try:
    from services.pay.stripe.client import StripeClient
    STRIPE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Stripe client not available: {e}")
    STRIPE_AVAILABLE = False

# Environment variables
YOOKASSA_PROVIDER_TOKEN = os.getenv("YOOKASSA_PROVIDER_TOKEN")

# Payment plans configuration - now imported from config
# PAYMENT_PLANS imported from config.py

async def create_invoice_message(message: types.Message, plan_id: str = "basic", user_id: int = None):
    """
    Create and send Telegram invoice message
    """
    try:
        # Use passed user_id or fallback to message.from_user.id
        if user_id is None:
            user_id = message.from_user.id
        
        username = message.from_user.username
        logger.info(f"=== CREATE_INVOICE_MESSAGE DEBUG ===")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Username: {username}")  
        logger.info(f"Message object type: {type(message)}")
        logger.info(f"Message from_user: {message.from_user}")
        logger.info(f"Plan: {plan_id}")
        logger.info(f"=====================================")
        
        if not YOOKASSA_PROVIDER_TOKEN:
            logger.error("YOOKASSA_PROVIDER_TOKEN is not set!")
            await message.answer("❌ Payment system is not configured. Please contact support.", reply_markup=create_main_menu_keyboard())
            return

        # Get user's language preference
        user = await get_or_create_user(user_id, username)
        user_language = user.get('language', 'en')
        
        # Get payment plans for user's language
        payment_plans = get_payment_plans_for_user_language(user_language)
        plan = payment_plans.get(plan_id)
        
        if not plan:
            logger.error(f"Invalid payment plan selected: {plan_id}")
            error_message = i18n.get_text("invoice_invalid_plan", user_language)
            await message.answer(error_message, reply_markup=create_main_menu_keyboard())
            return

        logger.info(f"[Telegram] Creating invoice: title={plan['title']}, price={plan['price']}, user_id={user_id}, provider_token={YOOKASSA_PROVIDER_TOKEN[:12]}..., payload=credits_{plan_id}_{user_id}")

        # Prepare provider_data for YooKassa receipt
        provider_data = json.dumps({
            "receipt": {
                "items": [
                    {
                        "description": plan["description"],
                        "quantity": 1,
                        "amount": {
                            "value": plan["price"] // 100,  # RUB, not kopecks
                            "currency": "RUB"
                        },
                        "vat_code": 1,
                        "payment_mode": "full_payment",
                        "payment_subject": "commodity"
                    }
                ],
                "tax_system_code": 1
            }
        })

        # Create invoice with translated content
        await message.answer_invoice(
            title=plan["title"],
            description=plan["description"],
            payload=f"credits_{plan_id}_{user_id}",
            provider_token=YOOKASSA_PROVIDER_TOKEN,
            currency=plan["currency"],
            prices=[
                types.LabeledPrice(
                    label=i18n.get_text("invoice_credits_label", user_language, credits=plan['credits']),
                    amount=plan["price"]
                )
            ],
            start_parameter=f"buy_{plan_id}",
            photo_url="https://api.c0r.ai/assets/logo_v2.png",
            photo_width=512,
            photo_height=512,
            need_email=True,
            send_email_to_provider=True,
            provider_data=provider_data,
            need_phone_number=False,  # Not used anymore
            need_shipping_address=False,
            is_flexible=False
        )
        
        success_message = i18n.get_text("invoice_created", user_language, user_id=user_id, plan_id=plan_id)
        logger.info(success_message)
        
    except Exception as e:
        logger.error(f"[Telegram] Failed to create invoice: {e!r}")
        logger.error(traceback.format_exc())
        
        # Get user's language for error message
        try:
            user = await get_or_create_user(user_id or message.from_user.id, message.from_user.username)
            user_language = user.get('language', 'en')
        except:
            user_language = 'en'
        
        error_message = i18n.get_text("invoice_failed", user_language, error=str(e))
        await message.answer(error_message, reply_markup=create_main_menu_keyboard())

async def handle_buy_callback(callback: types.CallbackQuery):
    """
    Handle callback from buy buttons
    """
    try:
        telegram_user_id = callback.from_user.id
        logger.info(f"Buy callback received from user {telegram_user_id} (@{callback.from_user.username})")
        logger.info(f"Callback data: {callback.data}")
        
        # Extract plan_id from callback data
        plan_id = callback.data.split("_")[1]  # "buy_basic" -> "basic"
        logger.info(f"Plan selected by user {telegram_user_id}: {plan_id}")
        
        # Answer callback to remove loading state
        await callback.answer()
        
        # Create invoice message with explicit user_id
        logger.info(f"Creating invoice for user {telegram_user_id}, plan {plan_id}")
        await create_invoice_message(callback.message, plan_id, user_id=telegram_user_id)
        
    except Exception as e:
        logger.error(f"Failed to handle buy callback: {e}")
        # Get user's language for error message
        try:
            user = await get_or_create_user(callback.from_user.id, callback.from_user.username)
            user_language = user.get('language', 'en')
        except:
            user_language = 'en'
        
        error_message = i18n.get_text("payment_error_message", user_language)
        await callback.answer(error_message)

async def handle_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    """
    Handle pre-checkout query - validate payment before processing
    """
    logger.info(f"=== PRE-CHECKOUT QUERY RECEIVED ===")
    logger.info(f"Pre-checkout query: {pre_checkout_query}")
    logger.info(f"From user: {pre_checkout_query.from_user.id}")
    logger.info(f"Payload: {pre_checkout_query.invoice_payload}")
    logger.info(f"Total amount: {pre_checkout_query.total_amount}")
    logger.info(f"Currency: {pre_checkout_query.currency}")
    logger.info(f"=====================================")
    
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
        
        # Get user's language for error messages
        user = await get_or_create_user(user_id)
        user_language = user.get('language', 'en') if user else 'en'
        
        # Validate plan exists
        payment_plans = get_payment_plans_for_user_language(user_language)
        plan = payment_plans.get(plan_id)
        if not plan:
            error_message = i18n.get_text("invoice_invalid_plan", user_language)
            await pre_checkout_query.answer(ok=False, error_message=error_message)
            return

        # Validate user exists
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
    logger.info(f"=== SUCCESSFUL PAYMENT RECEIVED ===")
    logger.info(f"Message: {message}")
    logger.info(f"From user: {message.from_user.id}")
    logger.info(f"Successful payment: {message.successful_payment}")
    logger.info(f"=====================================")
    
    try:
        payment = message.successful_payment
        payload = payment.invoice_payload
        telegram_user_id = message.from_user.id
        
        logger.info(f"Processing successful payment for user {telegram_user_id}")
        logger.info(f"Payment data: {payment}")
        logger.info(f"Payment payload: {payload}")
        
        # Parse payload to get plan and user info
        if not payload.startswith("credits_"):
            logger.error(f"Invalid payment payload for user {telegram_user_id}: {payload}")
            return

        parts = payload.split("_")
        if len(parts) != 3:
            logger.error(f"Invalid payment format for user {telegram_user_id}: {payload}")
            return

        plan_id = parts[1]
        user_id = int(parts[2])
        
        logger.info(f"Payment details - plan: {plan_id}, user_id: {user_id}, telegram_user_id: {telegram_user_id}")
        
        # Get user's language preference
        user = await get_or_create_user(user_id)
        user_language = user.get('language', 'en') if user else 'en'
        
        # Get plan details with user's language
        payment_plans = get_payment_plans_for_user_language(user_language)
        plan = payment_plans.get(plan_id)
        if not plan:
            logger.error(f"Invalid plan in payment for user {telegram_user_id}: {plan_id}")
            return

        logger.info(f"Plan details: {plan}")
        
        # Get user before adding credits
        user_before = await get_or_create_user(user_id)
        logger.info(f"User before payment: {user_before}")
        
        # Add credits to user account
        updated_user = await add_credits(user_id, plan["credits"])
        logger.info(f"User after payment: {updated_user}")
        
        # Add payment record to database
        payment_amount = payment.total_amount / 100  # Convert kopecks to rubles
        await add_payment(
            user_id=updated_user['id'],
            amount=payment_amount,
            gateway="telegram_payments",
            status="succeeded"
        )
        
        # Log payment action
        await log_user_action(
            user_id=updated_user['id'],
            action_type="payment_success",
            metadata={
                "plan_id": plan_id,
                "credits_added": plan["credits"],
                "amount_paid": payment_amount,
                "currency": payment.currency,
                "payment_charge_id": payment.telegram_payment_charge_id,
                "provider_payment_charge_id": payment.provider_payment_charge_id
            }
        )
        
        # Send confirmation message with translations
        success_title = i18n.get_text("payment_success_title", user_language)
        plan_title = plan['title']
        credits_added = i18n.get_text("payment_success_credits_added", user_language, credits=plan['credits'])
        amount_paid = f"{payment.total_amount/100:.2f} {payment.currency}"
        total_credits = i18n.get_text("payment_success_total_credits", user_language, total_credits=updated_user['credits_remaining'])
        continue_message = i18n.get_text("payment_success_continue", user_language)
        
        confirmation_message = (
            f"{success_title}\n\n"
            f"💳 **{plan_title}**\n"
            f"⚡ **{credits_added}**\n"
            f"💰 **Amount Paid**: {amount_paid}\n"
            f"🔋 **{total_credits}**\n\n"
            f"{continue_message}"
        )
        
        await message.answer(
            confirmation_message,
            parse_mode="Markdown",
            reply_markup=create_payment_success_keyboard()
        )
        
        logger.info(f"Payment processed successfully for user {user_id}: {plan['credits']} credits added, total credits: {updated_user['credits_remaining']}")
        
    except Exception as e:
        logger.error(f"Failed to process successful payment for user {telegram_user_id}: {e}")
        import traceback
        logger.error(f"Payment error traceback: {traceback.format_exc()}")
        
        # Get user's language for error message
        try:
            user = await get_or_create_user(telegram_user_id, message.from_user.username)
            user_language = user.get('language', 'en')
        except:
            user_language = 'en'
        
        error_message = i18n.get_text("payment_error_message", user_language)
        await message.answer(error_message) 