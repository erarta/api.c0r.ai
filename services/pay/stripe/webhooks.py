"""
Enhanced Stripe webhook handler for payment processing
"""
import json
import stripe
import os
import sys
from typing import Dict, Any, Tuple
from loguru import logger

# Add project root for imports
project_root = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, project_root)

try:
    from common.supabase_client import add_credits, add_payment, log_user_action
    from common.db.users import get_user_by_telegram_id
    SUPABASE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Supabase client not available: {e}")
    SUPABASE_AVAILABLE = False

from .client import StripeClient

class StripeWebhookHandler:
    def __init__(self):
        self.stripe_client = StripeClient()
        
    async def handle_webhook(self, payload: bytes, signature: str) -> Tuple[Dict[str, Any], int]:
        """
        Handle incoming Stripe webhook
        
        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
            
        Returns:
            Tuple of (response_data, status_code)
        """
        # Verify webhook signature
        if not await self.stripe_client.verify_webhook_signature(payload, signature):
            logger.error("Invalid webhook signature")
            return {'error': 'Invalid signature'}, 400
            
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, self.stripe_client.webhook_secret
            )
            
            logger.info(f"Processing Stripe webhook event: {event['type']}")
            
            # Handle different event types
            if event['type'] == 'checkout.session.completed':
                return await self.handle_checkout_completed(event['data']['object'])
            elif event['type'] == 'payment_intent.succeeded':
                return await self.handle_payment_succeeded(event['data']['object'])
            elif event['type'] == 'checkout.session.async_payment_succeeded':
                return await self.handle_async_payment_succeeded(event['data']['object'])
            elif event['type'] == 'payment_intent.payment_failed':
                return await self.handle_payment_failed(event['data']['object'])
            else:
                logger.info(f"Unhandled Stripe event: {event['type']}")
                return {'status': 'ignored', 'event_type': event['type']}, 200
                
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Stripe signature verification failed: {e}")
            return {'error': 'Invalid signature'}, 400
        except Exception as e:
            logger.error(f"Error processing Stripe webhook: {e}")
            import traceback
            traceback.print_exc()
            return {'error': 'Webhook processing failed'}, 500
    
    async def handle_checkout_completed(self, session: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Handle successful checkout completion
        
        Args:
            session: Stripe checkout session data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            logger.info(f"Processing checkout completion for session {session['id']}")
            
            # Extract metadata
            metadata = session.get('metadata', {})
            user_id = metadata.get('user_id')
            plan_id = metadata.get('plan_id')
            credits = metadata.get('credits')
            language = metadata.get('language', 'en')
            
            if not all([user_id, plan_id, credits]):
                logger.error(f"Missing required metadata in session {session['id']}: {metadata}")
                return {'error': 'Missing metadata'}, 400
            
            user_id = int(user_id)
            credits = int(credits)
            
            # Only process if payment was successful
            if session.get('payment_status') != 'paid':
                logger.warning(f"Session {session['id']} payment status is not 'paid': {session.get('payment_status')}")
                return {'status': 'pending', 'payment_status': session.get('payment_status')}, 200
            
            # Add credits and log payment if Supabase is available
            if SUPABASE_AVAILABLE:
                try:
                    # Verify user exists
                    user = await get_user_by_telegram_id(user_id)
                    if not user:
                        logger.error(f"User {user_id} not found in database")
                        return {'error': 'User not found'}, 404
                    
                    # Add credits to user account
                    await add_credits(user['id'], credits)
                    logger.info(f"Added {credits} credits to user {user_id}")
                    
                    # Log payment
                    await add_payment(
                        user_id=user['id'],
                        amount=session['amount_total'],
                        currency=session['currency'].upper(),
                        provider='stripe',
                        plan_id=plan_id,
                        transaction_id=session['id'],
                        status='completed'
                    )
                    logger.info(f"Logged Stripe payment for user {user_id}")
                    
                    # Log user action
                    await log_user_action(
                        user_id=user['id'],
                        action_type='stripe_payment_completed',
                        metadata={
                            'plan_id': plan_id,
                            'credits': credits,
                            'amount': session['amount_total'],
                            'currency': session['currency'],
                            'session_id': session['id'],
                            'language': language
                        }
                    )
                    
                    logger.info(f"Stripe payment completed successfully for user {user_id}, plan {plan_id}, {credits} credits")
                    
                except Exception as db_error:
                    logger.error(f"Database error processing payment: {db_error}")
                    return {'error': 'Database error'}, 500
            else:
                logger.warning("Supabase not available - payment logged locally only")
            
            return {
                'status': 'success',
                'user_id': user_id,
                'plan_id': plan_id,
                'credits': credits,
                'amount': session['amount_total'],
                'currency': session['currency'],
                'session_id': session['id']
            }, 200
            
        except Exception as e:
            logger.error(f"Error handling Stripe checkout completion: {e}")
            import traceback
            traceback.print_exc()
            return {'error': 'Payment processing failed'}, 500
    
    async def handle_payment_succeeded(self, payment_intent: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Handle successful payment intent
        
        Args:
            payment_intent: Stripe payment intent data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            logger.info(f"Processing payment intent success: {payment_intent['id']}")
            
            # Extract metadata
            metadata = payment_intent.get('metadata', {})
            user_id = metadata.get('user_id')
            
            if user_id:
                logger.info(f"Payment intent {payment_intent['id']} succeeded for user {user_id}")
            
            return {'status': 'success', 'payment_intent_id': payment_intent['id']}, 200
            
        except Exception as e:
            logger.error(f"Error handling payment intent success: {e}")
            return {'error': 'Payment intent processing failed'}, 500
    
    async def handle_async_payment_succeeded(self, session: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Handle successful async payment (e.g., bank transfers)
        
        Args:
            session: Stripe checkout session data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        logger.info(f"Processing async payment success for session {session['id']}")
        # Same logic as checkout completed
        return await self.handle_checkout_completed(session)
    
    async def handle_payment_failed(self, payment_intent: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Handle failed payment
        
        Args:
            payment_intent: Stripe payment intent data
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            logger.warning(f"Payment failed for intent {payment_intent['id']}")
            
            metadata = payment_intent.get('metadata', {})
            user_id = metadata.get('user_id')
            
            if user_id and SUPABASE_AVAILABLE:
                try:
                    # Log failed payment attempt
                    await log_user_action(
                        user_id=int(user_id),
                        action_type='stripe_payment_failed',
                        metadata={
                            'payment_intent_id': payment_intent['id'],
                            'amount': payment_intent['amount'],
                            'currency': payment_intent['currency'],
                            'failure_reason': payment_intent.get('last_payment_error', {}).get('message', 'Unknown')
                        }
                    )
                except Exception as e:
                    logger.error(f"Error logging payment failure: {e}")
            
            return {
                'status': 'failed', 
                'payment_intent_id': payment_intent['id'],
                'user_id': user_id
            }, 200
            
        except Exception as e:
            logger.error(f"Error handling payment failure: {e}")
            return {'error': 'Payment failure processing failed'}, 500

# FastAPI integration for webhook endpoints
try:
    from fastapi import Request, HTTPException
    
    async def stripe_webhook_endpoint(request: Request) -> Dict[str, Any]:
        """
        FastAPI endpoint for Stripe webhooks
        
        Args:
            request: FastAPI request object
            
        Returns:
            Response dictionary
        """
        try:
            payload = await request.body()
            signature = request.headers.get("stripe-signature")
            
            if not signature:
                raise HTTPException(status_code=400, detail="Missing Stripe signature")
            
            handler = StripeWebhookHandler()
            response_data, status_code = await handler.handle_webhook(payload, signature)
            
            if status_code != 200:
                raise HTTPException(status_code=status_code, detail=response_data)
            
            return response_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in webhook endpoint: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
            
except ImportError:
    logger.info("FastAPI not available - webhook endpoint not created")