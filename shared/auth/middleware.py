"""
Shared authentication utilities for inter-service communication
"""
import os
from functools import wraps
from fastapi import HTTPException, Request
from loguru import logger

# Internal API token for service-to-service communication
INTERNAL_API_TOKEN = os.getenv("INTERNAL_API_TOKEN")

def validate_internal_token(token: str) -> bool:
    """
    Validate internal API token for service-to-service communication
    
    Args:
        token: Token to validate
        
    Returns:
        bool: True if token is valid, False otherwise
    """
    if not INTERNAL_API_TOKEN:
        logger.error("INTERNAL_API_TOKEN not configured")
        return False
    
    if not token:
        logger.warning("No token provided")
        return False
    
    is_valid = token == INTERNAL_API_TOKEN
    if not is_valid:
        logger.warning(f"Invalid internal token provided: {token[:10]}...")
    
    return is_valid

def require_internal_auth(func):
    """
    Decorator to require internal authentication for FastAPI endpoints
    
    Usage:
        @app.post("/internal-endpoint")
        @require_internal_auth
        async def internal_endpoint(request: Request):
            # This endpoint requires X-Internal-Token header
            pass
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        # Extract token from header
        token = request.headers.get("X-Internal-Token")
        
        if not validate_internal_token(token):
            logger.warning(f"Unauthorized internal API access attempt from {request.client.host if request.client else 'unknown'}")
            raise HTTPException(
                status_code=401, 
                detail="Invalid or missing internal API token"
            )
        
        # Token is valid, proceed with the request
        return await func(request, *args, **kwargs)
    
    return wrapper

def get_auth_headers() -> dict:
    """
    Get headers for internal service requests
    
    Returns:
        dict: Headers with internal authentication token
    """
    if not INTERNAL_API_TOKEN:
        logger.error("INTERNAL_API_TOKEN not configured for outgoing requests")
        raise ValueError("Internal API token not configured")
    
    return {
        "X-Internal-Token": INTERNAL_API_TOKEN,
        "Content-Type": "application/json"
    }

class AuthenticationError(Exception):
    """Custom exception for authentication errors"""
    pass

def check_service_auth() -> None:
    """
    Check if service authentication is properly configured
    Raises AuthenticationError if not configured
    """
    if not INTERNAL_API_TOKEN:
        raise AuthenticationError("INTERNAL_API_TOKEN environment variable not set")
    
    if len(INTERNAL_API_TOKEN) < 32:
        raise AuthenticationError("INTERNAL_API_TOKEN should be at least 32 characters long")
    
    logger.info("Service authentication configured successfully")