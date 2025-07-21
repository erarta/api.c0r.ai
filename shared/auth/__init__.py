"""
Authentication module for inter-service communication
"""
from .middleware import (
    validate_internal_token,
    require_internal_auth,
    get_auth_headers,
    check_service_auth,
    AuthenticationError,
    INTERNAL_API_TOKEN
)

__all__ = [
    'validate_internal_token',
    'require_internal_auth', 
    'get_auth_headers',
    'check_service_auth',
    'AuthenticationError',
    'INTERNAL_API_TOKEN'
]