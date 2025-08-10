"""
Enhanced Stripe client with real API integration
"""
import stripe
import os
import sys
from typing import Dict, Any, Optional
from loguru import logger

# Add project root for imports
project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, project_root)

from common.config.payment_plans import get_payment_plans_for_region

# Configure Stripe (support both STRIPE_SECRET_KEY and STRIPE_API_KEY)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")

class StripeClient:
    def __init__(self):
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        self.api_key = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")
        
        if not self.api_key:
            logger.warning("STRIPE_SECRET_KEY not found in environment variables")
            
        if self.api_key:
            stripe.api_key = self.api_key
        
    async def create_checkout_session(
        self, 
        user_id: int, 
        plan_id: str, 
        language: str = "en",
        success_url: str = None,
        cancel_url: str = None
    ) -> Dict[str, Any]:
        """
        Create Stripe checkout session
        
        Args:
            user_id: Telegram user ID
            plan_id: Plan identifier ('basic' or 'pro')
            language: User's language for pricing
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect after cancelled payment
            
        Returns:
            Stripe checkout session data
        """
        try:
            # Get plan data for Stripe provider
            plans = get_payment_plans_for_region(language, provider='stripe')
            plan = plans.get(plan_id)
            
            if not plan:
                raise ValueError(f"Plan '{plan_id}' not found for Stripe provider")
            
            # Default URLs if not provided
            if not success_url:
                success_url = f"https://t.me/your_bot_username?start=payment_success_{plan_id}"
            if not cancel_url:
                cancel_url = f"https://t.me/your_bot_username?start=payment_cancel"
            
            # Create Stripe checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': plan['currency'].lower(),
                        'product_data': {
                            'name': plan['title'],
                            'description': plan['description'],
                            'images': ['https://api.c0r.ai/assets/logo_v2.png'],
                        },
                        'unit_amount': plan['price'],  # Amount in cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'user_id': str(user_id),
                    'plan_id': plan_id,
                    'credits': str(plan['credits']),
                    'telegram_user_id': str(user_id),
                    'language': language,
                    'provider': 'stripe'
                },
                customer_email=None,  # Will be collected during checkout
                billing_address_collection='auto',
                payment_intent_data={
                    'metadata': {
                        'user_id': str(user_id),
                        'plan_id': plan_id,
                        'credits': str(plan['credits']),
                    }
                }
            )
            
            logger.info(f"Created Stripe session {session.id} for user {user_id}, plan {plan_id}")
            return {
                'session_id': session.id,
                'checkout_url': session.url,
                'status': 'created',
                'plan_id': plan_id,
                'credits': plan['credits'],
                'amount': plan['price'],
                'currency': plan['currency'],
                'provider': 'stripe'
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe API error creating session: {e}")
            raise Exception(f"Payment system error: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating Stripe session: {e}")
            raise
    
    async def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify webhook signature for security
        
        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return True
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}")
            return False
    
    async def retrieve_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve Stripe checkout session
        
        Args:
            session_id: Stripe session ID
            
        Returns:
            Session data or None if not found
        """
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                'id': session.id,
                'status': session.status,
                'payment_status': session.payment_status,
                'amount_total': session.amount_total,
                'currency': session.currency,
                'metadata': session.metadata,
                'customer_email': session.customer_details.email if session.customer_details else None
            }
        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving Stripe session {session_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving session: {e}")
            return None
    
    async def list_payment_methods(self, customer_id: str) -> list:
        """
        List payment methods for customer
        
        Args:
            customer_id: Stripe customer ID
            
        Returns:
            List of payment methods
        """
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type="card",
            )
            return payment_methods.data
        except stripe.error.StripeError as e:
            logger.error(f"Error listing payment methods for {customer_id}: {e}")
            return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check Stripe API connectivity
        
        Returns:
            Health status information
        """
        try:
            if not self.api_key:
                return {
                    'status': 'error',
                    'message': 'Stripe API key not configured'
                }
            
            # Try to list a small number of payment intents to test connectivity
            stripe.PaymentIntent.list(limit=1)
            
            return {
                'status': 'healthy',
                'message': 'Stripe API accessible',
                'api_key_configured': bool(self.api_key),
                'webhook_secret_configured': bool(self.webhook_secret)
            }
            
        except stripe.error.AuthenticationError:
            return {
                'status': 'error',
                'message': 'Stripe API key invalid'
            }
        except stripe.error.StripeError as e:
            return {
                'status': 'error',
                'message': f'Stripe API error: {str(e)}'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Unknown error: {str(e)}'
            }

# Legacy function for backward compatibility
async def create_stripe_invoice(user_id: int, plan_id: str) -> dict:
    """
    DEPRECATED: Use StripeClient.create_checkout_session() instead
    """
    logger.warning("create_stripe_invoice is deprecated, use StripeClient.create_checkout_session()")
    
    client = StripeClient()
    try:
        session_data = await client.create_checkout_session(
            user_id=user_id,
            plan_id=plan_id
        )
        
        # Convert to legacy format
        return {
            "invoice_url": session_data['checkout_url'],
            "status": session_data['status'],
            "plan_id": session_data['plan_id'],
            "count": session_data['credits'],
            "amount": session_data['amount'],
            "recurring": False,  # Stripe sessions are one-time payments
            "session_id": session_data['session_id']
        }
    except Exception as e:
        logger.error(f"Error in legacy create_stripe_invoice: {e}")
        raise 