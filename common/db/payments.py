"""
Payment operations
Handles payment records and user payment history
"""
import asyncio
from typing import Optional, List, Dict, Any
from loguru import logger
from .client import supabase


async def add_payment(user_id: str, amount: float, gateway: str, status: str, metadata: Dict[str, Any] = None):
    """
    Add payment record to database
    
    Args:
        user_id: User UUID from database
        amount: Payment amount
        gateway: Payment gateway (stripe, yookassa)
        status: Payment status (pending, succeeded, failed, cancelled)
        metadata: Additional payment metadata
        
    Returns:
        True if payment recorded successfully
    """
    logger.info(f"Adding payment record for user {user_id}: {amount} via {gateway}")
    
    payment = {
        "user_id": user_id,
        "amount": amount,
        "gateway": gateway,
        "status": status,
        "metadata": metadata or {}
    }
    
    try:
        supabase.table("payments").insert(payment).execute()
        logger.info(f"Payment recorded for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to record payment for user {user_id}: {e}")
        return False


async def update_payment_status(payment_id: str, status: str, metadata: Dict[str, Any] = None):
    """
    Update payment status
    
    Args:
        payment_id: Payment ID from database
        status: New payment status
        metadata: Additional metadata to merge
        
    Returns:
        Updated payment record or None if failed
    """
    logger.info(f"Updating payment {payment_id} status to {status}")
    
    update_data = {"status": status}
    if metadata:
        update_data["metadata"] = metadata
    
    try:
        result = supabase.table("payments").update(update_data).eq("id", payment_id).execute()
        if result.data:
            logger.info(f"Payment {payment_id} status updated to {status}")
            return result.data[0]
        else:
            logger.warning(f"Payment {payment_id} not found for status update")
            return None
    except Exception as e:
        logger.error(f"Failed to update payment {payment_id} status: {e}")
        return None


async def get_user_total_paid(user_id: str) -> float:
    """
    Calculate total amount paid by user from payments table
    
    Args:
        user_id: User UUID from database
        
    Returns:
        Total amount paid by user
    """
    try:
        logger.info(f"Calculating total paid for user {user_id}")
        
        # Get all successful payments for user
        payments = supabase.table("payments").select("amount").eq("user_id", user_id).eq("status", "succeeded").execute().data
        
        total = sum(float(payment['amount']) for payment in payments)
        logger.info(f"Total paid for user {user_id}: {total}")
        
        return total
    except Exception as e:
        logger.error(f"Error calculating total paid for user {user_id}: {e}")
        return 0.0


async def get_user_payment_history(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get user's payment history
    
    Args:
        user_id: User UUID from database
        limit: Maximum number of payments to return
        
    Returns:
        List of payment records
    """
    logger.info(f"Getting payment history for user {user_id}, limit: {limit}")
    
    try:
        result = supabase.table("payments").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        logger.info(f"Retrieved {len(result.data)} payments for user {user_id}")
        return result.data
    except Exception as e:
        logger.error(f"Failed to get payment history for user {user_id}: {e}")
        return []


async def get_payment_by_id(payment_id: str) -> Optional[Dict[str, Any]]:
    """
    Get payment record by ID
    
    Args:
        payment_id: Payment ID from database
        
    Returns:
        Payment record or None if not found
    """
    logger.info(f"Getting payment by ID: {payment_id}")
    
    try:
        result = supabase.table("payments").select("*").eq("id", payment_id).execute()
        if result.data:
            logger.info(f"Found payment {payment_id}")
            return result.data[0]
        else:
            logger.warning(f"Payment {payment_id} not found")
            return None
    except Exception as e:
        logger.error(f"Failed to get payment {payment_id}: {e}")
        return None


async def get_payments_by_status(status: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get payments by status
    
    Args:
        status: Payment status to filter by
        limit: Maximum number of payments to return
        
    Returns:
        List of payment records
    """
    logger.info(f"Getting payments with status: {status}, limit: {limit}")
    
    try:
        result = supabase.table("payments").select("*").eq("status", status).order("created_at", desc=True).limit(limit).execute()
        logger.info(f"Retrieved {len(result.data)} payments with status {status}")
        return result.data
    except Exception as e:
        logger.error(f"Failed to get payments with status {status}: {e}")
        return []


async def get_payments_by_gateway(gateway: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get payments by gateway
    
    Args:
        gateway: Payment gateway to filter by
        limit: Maximum number of payments to return
        
    Returns:
        List of payment records
    """
    logger.info(f"Getting payments for gateway: {gateway}, limit: {limit}")
    
    try:
        result = supabase.table("payments").select("*").eq("gateway", gateway).order("created_at", desc=True).limit(limit).execute()
        logger.info(f"Retrieved {len(result.data)} payments for gateway {gateway}")
        return result.data
    except Exception as e:
        logger.error(f"Failed to get payments for gateway {gateway}: {e}")
        return []


async def get_payment_statistics(date_from: str = None, date_to: str = None) -> Dict[str, Any]:
    """
    Get payment statistics
    
    Args:
        date_from: Start date filter (YYYY-MM-DD format)
        date_to: End date filter (YYYY-MM-DD format)
        
    Returns:
        Dictionary with payment statistics
    """
    logger.info(f"Getting payment statistics from {date_from} to {date_to}")
    
    try:
        query = supabase.table("payments").select("*")
        
        if date_from:
            query = query.gte("created_at", f"{date_from}T00:00:00")
        if date_to:
            query = query.lt("created_at", f"{date_to}T23:59:59")
        
        payments = query.execute().data
        
        # Calculate statistics
        total_payments = len(payments)
        successful_payments = [p for p in payments if p['status'] == 'succeeded']
        failed_payments = [p for p in payments if p['status'] == 'failed']
        pending_payments = [p for p in payments if p['status'] == 'pending']
        
        total_revenue = sum(float(p['amount']) for p in successful_payments)
        
        # Group by gateway
        gateway_stats = {}
        for payment in payments:
            gateway = payment['gateway']
            if gateway not in gateway_stats:
                gateway_stats[gateway] = {'count': 0, 'revenue': 0}
            gateway_stats[gateway]['count'] += 1
            if payment['status'] == 'succeeded':
                gateway_stats[gateway]['revenue'] += float(payment['amount'])
        
        stats = {
            'total_payments': total_payments,
            'successful_payments': len(successful_payments),
            'failed_payments': len(failed_payments),
            'pending_payments': len(pending_payments),
            'success_rate': len(successful_payments) / total_payments * 100 if total_payments > 0 else 0,
            'total_revenue': total_revenue,
            'average_payment': total_revenue / len(successful_payments) if successful_payments else 0,
            'gateway_stats': gateway_stats,
            'date_from': date_from,
            'date_to': date_to
        }
        
        logger.info(f"Payment statistics calculated: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get payment statistics: {e}")
        return {
            'total_payments': 0,
            'successful_payments': 0,
            'failed_payments': 0,
            'pending_payments': 0,
            'success_rate': 0,
            'total_revenue': 0,
            'average_payment': 0,
            'gateway_stats': {},
            'error': str(e)
        }


async def find_payment_by_external_id(external_id: str, gateway: str) -> Optional[Dict[str, Any]]:
    """
    Find payment by external payment ID (from Stripe, YooKassa, etc.)
    
    Args:
        external_id: External payment ID
        gateway: Payment gateway
        
    Returns:
        Payment record or None if not found
    """
    logger.info(f"Finding payment by external ID: {external_id} for gateway: {gateway}")
    
    try:
        # Search in metadata for external_id
        result = supabase.table("payments").select("*").eq("gateway", gateway).execute()
        
        for payment in result.data:
            metadata = payment.get('metadata', {})
            if metadata.get('external_id') == external_id or metadata.get('payment_id') == external_id:
                logger.info(f"Found payment by external ID: {external_id}")
                return payment
        
        logger.warning(f"Payment not found by external ID: {external_id}")
        return None
        
    except Exception as e:
        logger.error(f"Failed to find payment by external ID {external_id}: {e}")
        return None