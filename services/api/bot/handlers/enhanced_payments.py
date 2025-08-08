"""
Enhanced Payment Handler for multiple payment providers
Supports YooKassa, Stripe, and Telegram Stars
"""
import os
import sys
from aiogram import types
from loguru import logger
from common.supabase_client import get_or_create_user, add_credits, add_payment, log_user_action
from .keyboards import create_main_menu_keyboard, create_payment_success_keyboard
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
    logger.info("✅ Stripe client imported successfully")
except ImportError as e:
    logger.warning(f"❌ Stripe client not available: {e}")
    STRIPE_AVAILABLE = False

# Import legacy YooKassa function
from .payments import create_invoice_message

class EnhancedPaymentHandler:
    """
    Enhanced payment handler supporting multiple payment providers
    """
    
    def __init__(self):
        if STRIPE_AVAILABLE:
            try:
                self.stripe_client = StripeClient()
                logger.info("✅ Stripe client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Stripe client: {e}")
                self.stripe_client = None
        else:
            self.stripe_client = None
            logger.warning("❌ Stripe client not available - using None")
        
    async def show_payment_options(self, message: types.Message):
        """
        Show appropriate payment options based on user's region
        """
        try:
            user_id = message.from_user.id
            username = message.from_user.username
            telegram_user = message.from_user
            telegram_language_code = telegram_user.language_code or "unknown"
            
            user = await get_or_create_user(user_id, username)
            user_language = user.get('language', 'en')
            
            # 🔍 DEBUG: Payment Routing Analysis
            is_cis = is_cis_region(user_language)
            payment_provider = get_payment_provider(user_language)
            available_providers = get_available_payment_providers(user_language)
            
            # Log detailed debug information
            logger.info(f"🔍 PAYMENT DEBUG for user {user_id}:")
            logger.info(f"   Telegram language_code: {telegram_language_code}")
            logger.info(f"   User DB language: {user_language}")
            logger.info(f"   Is CIS region: {is_cis}")
            logger.info(f"   Payment provider: {payment_provider}")
            logger.info(f"   Available providers: {available_providers}")
            
            # Print to terminal for immediate visibility
            print(f"\n🔍 PAYMENT DEBUG for user {user_id}:")
            print(f"   Telegram language_code: {telegram_language_code}")
            print(f"   User DB language: {user_language}")
            print(f"   Is CIS region: {is_cis}")
            print(f"   Payment provider: {payment_provider}")
            print(f"   Available providers: {available_providers}")
            print("=" * 50)
            
            logger.info(f"Showing payment options for user {user_id}, language: {user_language}")
            
            # Get available providers for user's region
            available_providers = get_available_payment_providers(user_language)
            
            if not available_providers:
                await message.answer(
                    i18n.get_text("error_no_payment_providers", user_language),
                    reply_markup=create_main_menu_keyboard()
                )
                return
            
            # Show payment options based on region
            if is_cis_region(user_language):
                # CIS users - YooKassa only
                await self.show_yookassa_payment_options(message, user_language)
            else:
                # International users - Stripe + Telegram Stars
                await self.show_international_payment_options(message, user_language)
                
        except Exception as e:
            logger.error(f"Error showing payment options: {e}")
            await message.answer(
                i18n.get_text("error_payment_options", user_language or "en"),
                reply_markup=create_main_menu_keyboard()
            )
    
    async def show_yookassa_payment_options(self, message: types.Message, language: str):
        """
        Show YooKassa payment options for CIS users
        """
        try:
            # Get YooKassa plans
            payment_plans = get_payment_plans_for_region(language, provider='yookassa')
            
            # Create inline keyboard with payment options
            keyboard_buttons = []
            
            for plan_id, plan in payment_plans.items():
                price_display = f"{plan['price']/100:.0f} ₽"
                button_text = f"{plan['title']} - {plan['credits']} credits - {price_display}"
                
                keyboard_buttons.append([
                    types.InlineKeyboardButton(
                        text=button_text,
                        callback_data=f"yookassa_pay_{plan_id}"
                    )
                ])
            
            # Add back button
            keyboard_buttons.append([
                types.InlineKeyboardButton(
                    text=i18n.get_text("btn_back", language),
                    callback_data="action_main_menu"
                )
            ])
            
            # Create keyboard with inline_keyboard parameter
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            # Send payment options message
            message_text = i18n.get_text("payment_options_title", language)
            await message.answer(message_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error showing YooKassa payment options: {e}")
            await message.answer(
                i18n.get_text("error_payment_options", language),
                reply_markup=create_main_menu_keyboard()
            )
    
    async def show_international_payment_options(self, message: types.Message, language: str):
        """
        Show payment system selection (Stripe or Telegram Stars)
        """
        try:
            # Get user data to show current credits
            user_id = message.from_user.id
            user = await get_or_create_user(user_id)
            current_credits = user.get('credits_remaining', 0)
            
            # Create inline keyboard for payment system selection
            keyboard_buttons = [
                [
                    types.InlineKeyboardButton(
                        text="💳 Credit Card (Stripe)",
                        callback_data="payment_system_stripe"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text="⭐ Telegram Stars",
                        callback_data="payment_system_stars"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text=i18n.get_text("btn_back", language),
                        callback_data="action_main_menu"
                    )
                ]
            ]
            
            # Create keyboard with inline_keyboard parameter
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            # Send payment system selection message with current credits
            message_text = i18n.get_text("payment_system_selection", language, credits=current_credits)
            await message.answer(message_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error showing payment system selection: {e}")
            await message.answer(
                i18n.get_text("error_payment_options", language),
                reply_markup=create_main_menu_keyboard()
            )
    
    async def show_stripe_payment_plans(self, message: types.Message, language: str):
        """
        Show Stripe payment plans
        """
        try:
            # Get Stripe plans
            stripe_plans = get_payment_plans_for_region(language, provider='stripe')
            
            # Create inline keyboard with Stripe payment options
            keyboard_buttons = []
            
            for plan_id, plan in stripe_plans.items():
                price_display = f"${plan['price']/100:.2f}"
                button_text = f"{plan['title']} - {plan['credits']} credits - {price_display}"
                
                keyboard_buttons.append([
                    types.InlineKeyboardButton(
                        text=button_text,
                        callback_data=f"stripe_pay_{plan_id}"
                    )
                ])
            
            # Add back button
            keyboard_buttons.append([
                types.InlineKeyboardButton(
                    text=i18n.get_text("btn_back", language),
                    callback_data="payment_system_selection"
                )
            ])
            
            # Create keyboard with inline_keyboard parameter
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            # Send Stripe payment options message
            message_text = i18n.get_text("stripe_payment_plans", language)
            await message.answer(message_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error showing Stripe payment plans: {e}")
            await message.answer(
                i18n.get_text("error_payment_options", language),
                reply_markup=create_main_menu_keyboard()
            )
    
    async def show_stars_payment_plans(self, message: types.Message, language: str):
        """
        Show Telegram Stars payment plans
        """
        try:
            # Get Telegram Stars plans
            stars_plans = get_payment_plans_for_region(language, provider='telegram_stars')
            
            # Create inline keyboard with Stars payment options
            keyboard_buttons = []
            
            for plan_id, plan in stars_plans.items():
                price_display = f"{plan['price']} ⭐"
                button_text = f"{plan['title']} - {plan['credits']} credits - {price_display}"
                
                keyboard_buttons.append([
                    types.InlineKeyboardButton(
                        text=button_text,
                        callback_data=f"stars_pay_{plan_id}"
                    )
                ])
            
            # Add back button
            keyboard_buttons.append([
                types.InlineKeyboardButton(
                    text=i18n.get_text("btn_back", language),
                    callback_data="payment_system_selection"
                )
            ])
            
            # Create keyboard with inline_keyboard parameter
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            
            # Send Stars payment options message
            message_text = i18n.get_text("stars_payment_plans", language)
            await message.answer(message_text, reply_markup=keyboard)
            
        except Exception as e:
            logger.error(f"Error showing Stars payment plans: {e}")
            await message.answer(
                i18n.get_text("error_payment_options", language),
                reply_markup=create_main_menu_keyboard()
            )
    
    async def handle_payment_callback(self, callback: types.CallbackQuery):
        """
        Handle payment button clicks for all providers
        """
        try:
            user_id = callback.from_user.id
            username = callback.from_user.username
            user = await get_or_create_user(user_id, username)
            user_language = user.get('language', 'en')
            
            # Parse callback data
            callback_data = callback.data
            callback_parts = callback_data.split('_')
            
            logger.info(f"Payment callback: {callback_data}, user={user_id}")
            
            # Handle payment system selection
            if callback_data == "payment_system_stripe":
                await self.show_stripe_payment_plans(callback.message, user_language)
                await callback.answer()
                return
            elif callback_data == "payment_system_stars":
                await self.show_stars_payment_plans(callback.message, user_language)
                await callback.answer()
                return
            elif callback_data == "payment_system_selection":
                # Get user data to show current credits
                user = await get_or_create_user(user_id)
                current_credits = user.get('credits_remaining', 0)
                
                # Create inline keyboard for payment system selection
                keyboard_buttons = [
                    [
                        types.InlineKeyboardButton(
                            text="💳 Credit Card (Stripe)",
                            callback_data="payment_system_stripe"
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text="⭐ Telegram Stars",
                            callback_data="payment_system_stars"
                        )
                    ],
                    [
                        types.InlineKeyboardButton(
                            text=i18n.get_text("btn_back", user_language),
                            callback_data="action_main_menu"
                        )
                    ]
                ]
                
                # Create keyboard with inline_keyboard parameter
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
                
                # Send payment system selection message with current credits
                message_text = i18n.get_text("payment_system_selection", user_language, credits=current_credits)
                await callback.message.answer(message_text, reply_markup=keyboard)
                await callback.answer()
                return
            
            # Handle payment plan selection
            if len(callback_parts) < 3:
                await callback.answer("Invalid payment option")
                return
            
            provider = callback_parts[0]
            action = callback_parts[1]
            plan_id = callback_parts[2]
            
            logger.info(f"Payment plan callback: provider={provider}, action={action}, plan={plan_id}, user={user_id}")
            
            if provider == "yookassa" and action == "pay":
                await self.handle_yookassa_payment(callback, plan_id, user_language)
            elif provider == "stripe" and action == "pay":
                await self.handle_stripe_payment(callback, plan_id, user_language)
            elif provider == "stars" and action == "pay":
                await self.handle_telegram_stars_payment(callback, plan_id, user_language)
            else:
                await callback.answer("Payment method not implemented yet")
                
        except Exception as e:
            logger.error(f"Error handling payment callback: {e}")
            await callback.answer("Payment error occurred")
    
    async def handle_yookassa_payment(self, callback: types.CallbackQuery, plan_id: str, language: str):
        """
        Handle YooKassa payment - use existing create_invoice_message function
        """
        try:
            # Call existing YooKassa invoice creation
            await create_invoice_message(callback.message, plan_id, callback.from_user.id)
            await callback.answer()
        except Exception as e:
            logger.error(f"Error handling YooKassa payment: {e}")
            await callback.answer("YooKassa payment error")
    
    async def handle_stripe_payment(self, callback: types.CallbackQuery, plan_id: str, language: str):
        """
        Handle Stripe payment
        """
        try:
            logger.info(f"🔍 Stripe payment debug:")
            logger.info(f"   STRIPE_AVAILABLE: {STRIPE_AVAILABLE}")
            logger.info(f"   self.stripe_client: {self.stripe_client}")
            logger.info(f"   plan_id: {plan_id}")
            logger.info(f"   language: {language}")
            
            if not STRIPE_AVAILABLE:
                logger.error("❌ Stripe not available - STRIPE_AVAILABLE is False")
                await callback.answer("Stripe not available")
                return
                
            if not self.stripe_client:
                logger.error("❌ Stripe client is None")
                await callback.answer("Stripe not available")
                return
            
            user_id = callback.from_user.id
            
            # Create Stripe checkout session
            success_url = f"https://t.me/your_bot_username?start=payment_success_{plan_id}"
            cancel_url = f"https://t.me/your_bot_username?start=payment_cancel"
            
            session_data = await self.stripe_client.create_checkout_session(
                user_id=user_id,
                plan_id=plan_id,
                language=language,
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            # Send checkout URL to user
            checkout_message = i18n.get_text("stripe_checkout_message", language)
            payment_button = types.InlineKeyboardMarkup(inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="💳 Pay with Stripe",
                        url=session_data['checkout_url']
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text=i18n.get_text("btn_back", language),
                        callback_data="action_main_menu"
                    )
                ]
            ])
            
            await callback.message.answer(
                f"{checkout_message}\n\n💳 **Secure Payment via Stripe**\n"
                f"Plan: {session_data['plan_id'].title()}\n"
                f"Credits: {session_data['credits']}\n"
                f"Amount: ${session_data['amount']/100:.2f}",
                reply_markup=payment_button,
                parse_mode="Markdown"
            )
            
            await callback.answer()
            
        except Exception as e:
            logger.error(f"Error handling Stripe payment: {e}")
            await callback.answer("Stripe payment error")
    
    async def handle_telegram_stars_payment(self, callback: types.CallbackQuery, plan_id: str, language: str):
        """
        Handle Telegram Stars payment
        """
        try:
            # Get plan data
            plans = get_payment_plans_for_region(language, provider='telegram_stars')
            plan = plans.get(plan_id)
            
            if not plan:
                await callback.answer("Plan not found")
                return
            
            user_id = callback.from_user.id
            
            # Create Telegram Stars invoice
            await callback.message.answer_invoice(
                title=plan["title"],
                description=plan["description"],
                payload=f"stars_{plan_id}_{user_id}",
                provider_token="",  # Empty for Telegram Stars
                currency="XTR",  # Telegram Stars currency
                prices=[
                    types.LabeledPrice(
                        label=f"{plan['credits']} credits",
                        amount=plan["price"]  # Amount in stars
                    )
                ],
                start_parameter=f"stars_{plan_id}",
                photo_url="https://api.c0r.ai/assets/logo_v2.png",
                photo_width=512,
                photo_height=512,
            )
            
            await callback.answer()
            
        except Exception as e:
            logger.error(f"Error handling Telegram Stars payment: {e}")
            await callback.answer("Telegram Stars payment error")

# Create global payment handler instance
enhanced_payment_handler = EnhancedPaymentHandler()
