"""
User action logging operations
Handles logging of all user actions and photo analyses
"""
import asyncio
from typing import Optional, Dict, Any
from loguru import logger
from .client import supabase


async def log_user_action(user_id: str, action_type: str, metadata: Dict[str, Any] = None, photo_url: str = None, kbzhu: Dict[str, Any] = None, model_used: str = None):
    """
    Universal function to log all user actions
    
    Args:
        user_id: User UUID from database
        action_type: Type of action (start, help, status, buy, photo_analysis, profile, daily)
        metadata: Additional action-specific data
        photo_url: URL of photo (for photo_analysis only)
        kbzhu: Nutritional data (for photo_analysis only)
        model_used: AI model used (for photo_analysis only)
        
    Returns:
        True if logged successfully
    """
    logger.info(f"Logging user action: {action_type} for user {user_id}")
    
    log = {
        "user_id": user_id,
        "action_type": action_type,
        "metadata": metadata or {}
    }
    
    # Add photo-specific data if provided
    if photo_url:
        log["photo_url"] = photo_url
    if kbzhu:
        log["kbzhu"] = kbzhu
    if model_used:
        log["model_used"] = model_used
    
    try:
        supabase.table("logs").insert(log).execute()
        logger.info(f"Action {action_type} logged for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to log action {action_type} for user {user_id}: {e}")
        return False


async def log_analysis(user_id: str, photo_url: str, kbzhu: Dict[str, Any], model_used: str):
    """
    Legacy function for photo analysis logging - now uses log_user_action
    
    Args:
        user_id: User UUID from database
        photo_url: URL of analyzed photo
        kbzhu: Nutritional data from analysis
        model_used: AI model used for analysis
        
    Returns:
        True if logged successfully
    """
    logger.info(f"Logging analysis for user {user_id}")
    return await log_user_action(
        user_id=user_id,
        action_type="photo_analysis",
        photo_url=photo_url,
        kbzhu=kbzhu,
        model_used=model_used
    )


async def log_bot_command(user_id: str, command: str, metadata: Dict[str, Any] = None):
    """
    Log bot command usage
    
    Args:
        user_id: User UUID from database
        command: Command name (start, help, status, etc.)
        metadata: Additional command-specific data
        
    Returns:
        True if logged successfully
    """
    return await log_user_action(
        user_id=user_id,
        action_type=command,
        metadata=metadata
    )


async def log_payment_attempt(user_id: str, plan_id: str, gateway: str, amount: float, metadata: Dict[str, Any] = None):
    """
    Log payment attempt
    
    Args:
        user_id: User UUID from database
        plan_id: Payment plan ID (basic, pro)
        gateway: Payment gateway (stripe, yookassa)
        amount: Payment amount
        metadata: Additional payment data
        
    Returns:
        True if logged successfully
    """
    payment_metadata = {
        "plan_id": plan_id,
        "gateway": gateway,
        "amount": amount,
        **(metadata or {})
    }
    
    return await log_user_action(
        user_id=user_id,
        action_type="payment_attempt",
        metadata=payment_metadata
    )


async def log_profile_update(user_id: str, updated_fields: list, metadata: Dict[str, Any] = None):
    """
    Log profile update
    
    Args:
        user_id: User UUID from database
        updated_fields: List of fields that were updated
        metadata: Additional profile data
        
    Returns:
        True if logged successfully
    """
    profile_metadata = {
        "updated_fields": updated_fields,
        **(metadata or {})
    }
    
    return await log_user_action(
        user_id=user_id,
        action_type="profile_update",
        metadata=profile_metadata
    )


async def get_user_action_history(user_id: str, action_type: str = None, limit: int = 50):
    """
    Get user's action history
    
    Args:
        user_id: User UUID from database
        action_type: Filter by specific action type (optional)
        limit: Maximum number of records to return
        
    Returns:
        List of user actions
    """
    logger.info(f"Getting action history for user {user_id}, type: {action_type}, limit: {limit}")
    
    query = supabase.table("logs").select("*").eq("user_id", user_id).order("timestamp", desc=True).limit(limit)
    
    if action_type:
        query = query.eq("action_type", action_type)
    
    try:
        result = query.execute()
        logger.info(f"Retrieved {len(result.data)} actions for user {user_id}")
        return result.data
    except Exception as e:
        logger.error(f"Failed to get action history for user {user_id}: {e}")
        return []


async def get_user_analysis_count(user_id: str, date_from: str = None, date_to: str = None) -> int:
    """
    Get count of user's photo analyses
    
    Args:
        user_id: User UUID from database
        date_from: Start date filter (YYYY-MM-DD format)
        date_to: End date filter (YYYY-MM-DD format)
        
    Returns:
        Number of analyses
    """
    logger.info(f"Getting analysis count for user {user_id}")
    
    query = supabase.table("logs").select("id", count="exact").eq("user_id", user_id).eq("action_type", "photo_analysis")
    
    if date_from:
        query = query.gte("timestamp", f"{date_from}T00:00:00")
    if date_to:
        query = query.lt("timestamp", f"{date_to}T23:59:59")
    
    try:
        result = query.execute()
        count = result.count or 0
        logger.info(f"Analysis count for user {user_id}: {count}")
        return count
    except Exception as e:
        logger.error(f"Failed to get analysis count for user {user_id}: {e}")
        return 0


async def get_popular_actions(limit: int = 10):
    """
    Get most popular user actions
    
    Args:
        limit: Maximum number of actions to return
        
    Returns:
        List of actions with counts
    """
    logger.info(f"Getting popular actions, limit: {limit}")
    
    try:
        # This would need a more complex query in production
        # For now, return basic action types
        result = supabase.table("logs").select("action_type", count="exact").execute()
        
        # Group by action_type would need to be done in application code
        # or with a more sophisticated query
        logger.info(f"Retrieved action statistics")
        return result.data
    except Exception as e:
        logger.error(f"Failed to get popular actions: {e}")
        return []


async def cleanup_old_logs(days_to_keep: int = 90):
    """
    Clean up old log entries
    
    Args:
        days_to_keep: Number of days to keep logs
        
    Returns:
        Number of deleted records
    """
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    cutoff_str = cutoff_date.strftime('%Y-%m-%dT%H:%M:%S')
    
    logger.info(f"Cleaning up logs older than {cutoff_str}")
    
    try:
        result = supabase.table("logs").delete().lt("timestamp", cutoff_str).execute()
        deleted_count = len(result.data) if result.data else 0
        logger.info(f"Deleted {deleted_count} old log entries")
        return deleted_count
    except Exception as e:
        logger.error(f"Failed to cleanup old logs: {e}")
        return 0

# --- Analysis correction helpers ---

def get_log_by_id(user_id: str, log_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a single log row by id for a specific user"""
    try:
        res = supabase.table("logs").select("*").eq("user_id", user_id).eq("id", log_id).single().execute()
        return res.data
    except Exception as e:
        logger.error(f"Failed to get log {log_id} for user {user_id}: {e}")
        return None


def get_latest_photo_analysis_log_id(user_id: str) -> Optional[str]:
    """Return most recent photo_analysis log id for a user"""
    try:
        res = (
            supabase
            .table("logs")
            .select("id")
            .eq("user_id", user_id)
            .eq("action_type", "photo_analysis")
            .order("timestamp", desc=True)
            .limit(1)
            .execute()
        )
        if res.data:
            return res.data[0]["id"]
        return None
    except Exception as e:
        logger.error(f"Failed to get latest analysis log for user {user_id}: {e}")
        return None


def extract_log_calories(log_row: Dict[str, Any]) -> Optional[float]:
    """
    Try to extract the original calories from a log row.
    Priority: kbzhu.calories → metadata.analysis.total_nutrition.calories
    """
    try:
        kbzhu = log_row.get("kbzhu")
        if isinstance(kbzhu, dict) and "calories" in kbzhu:
            return float(kbzhu["calories"])  # type: ignore[arg-type]
    except Exception:
        pass
    try:
        meta = log_row.get("metadata") or {}
        analysis = meta.get("analysis") if isinstance(meta, dict) else None
        if isinstance(analysis, dict):
            tn = analysis.get("total_nutrition")
            if isinstance(tn, dict) and "calories" in tn:
                return float(tn["calories"])  # type: ignore[arg-type]
    except Exception:
        pass
    return None


def get_effective_log_calories(log_row: Dict[str, Any]) -> Optional[float]:
    """Return corrected calories if present, else original calories."""
    meta = log_row.get("metadata") or {}
    corrected = None
    if isinstance(meta, dict):
        corrected = meta.get("corrected_total_calories")
    if corrected is not None:
        try:
            return float(corrected)
        except Exception:
            pass
    return extract_log_calories(log_row)


def set_analysis_corrected_calories(user_id: str, log_id: str, corrected_calories: float) -> bool:
    """
    Persist corrected calories into logs.metadata.corrected_total_calories.
    """
    try:
        row = get_log_by_id(user_id, log_id)
        if not row:
            return False
        metadata = row.get("metadata") or {}
        if not isinstance(metadata, dict):
            metadata = {}
        metadata["corrected_total_calories"] = float(corrected_calories)
        supabase.table("logs").update({"metadata": metadata}).eq("id", log_id).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        logger.error(f"Failed to set corrected calories for log {log_id}: {e}")
        return False