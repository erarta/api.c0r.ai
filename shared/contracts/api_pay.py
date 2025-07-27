"""
API ↔ Payment Service Contract
Defines the interface between API service and Payment service
"""

from typing import Dict, Any
from ..models.payment import InvoiceRequest, InvoiceResponse, PaymentRequest, PaymentResponse
from ..models.user import UserCreditsRequest, UserCreditsResponse
from ..models.common import BaseResponse, ErrorResponse


class APIPayContract:
    """Contract for API service to Payment service communication"""
    
    # === Invoice Creation ===
    
    @staticmethod
    def create_invoice_request(
        user_id: str,
        amount: float,
        description: str,
        plan_id: str = "basic",
        currency: str = "RUB"
    ) -> InvoiceRequest:
        """
        Create request for payment invoice
        
        Args:
            user_id: User ID (telegram_id as string)
            amount: Payment amount
            description: Payment description
            plan_id: Payment plan identifier
            currency: Currency code
            
        Returns:
            InvoiceRequest: Validated request model
        """
        return InvoiceRequest(
            user_id=user_id,
            amount=amount,
            description=description,
            plan_id=plan_id,
            currency=currency
        )
    
    @staticmethod
    def create_invoice_response(response_data: Dict[str, Any]) -> InvoiceResponse:
        """
        Parse Payment service response for invoice creation
        
        Args:
            response_data: Raw response from Payment service
            
        Returns:
            InvoiceResponse: Validated response model
        """
        return InvoiceResponse(**response_data)
    
    # === Credit Management ===
    
    @staticmethod
    def add_credits_request(
        user_id: str,
        count: int = 20,
        payment_id: str = None,
        amount: float = None,
        gateway: str = "yookassa",
        status: str = "succeeded"
    ) -> UserCreditsRequest:
        """
        Create request for adding credits to user
        
        Args:
            user_id: User ID (telegram_id as string)
            count: Number of credits to add
            payment_id: Payment ID for tracking
            amount: Payment amount
            gateway: Payment gateway
            status: Payment status
            
        Returns:
            UserCreditsRequest: Validated request model
        """
        return UserCreditsRequest(
            user_id=user_id,
            count=count,
            payment_id=payment_id,
            amount=amount,
            gateway=gateway,
            status=status
        )
    
    @staticmethod
    def add_credits_response(response_data: Dict[str, Any]) -> UserCreditsResponse:
        """
        Parse API service response for credits addition
        
        Args:
            response_data: Raw response from API service
            
        Returns:
            UserCreditsResponse: Validated response model
        """
        return UserCreditsResponse(**response_data)
    
    # === Payment Processing ===
    
    @staticmethod
    def process_payment_request(
        user_id: str,
        payment_id: str,
        amount: float,
        gateway: str,
        status: str,
        metadata: Dict[str, Any] = None
    ) -> PaymentRequest:
        """
        Create request for payment processing
        
        Args:
            user_id: User ID
            payment_id: Payment ID from gateway
            amount: Payment amount
            gateway: Payment gateway
            status: Payment status
            metadata: Additional payment metadata
            
        Returns:
            PaymentRequest: Validated request model
        """
        return PaymentRequest(
            user_id=user_id,
            payment_id=payment_id,
            amount=amount,
            gateway=gateway,
            status=status,
            metadata=metadata
        )
    
    @staticmethod
    def process_payment_response(response_data: Dict[str, Any]) -> PaymentResponse:
        """
        Parse Payment service response for payment processing
        
        Args:
            response_data: Raw response from Payment service
            
        Returns:
            PaymentResponse: Validated response model
        """
        return PaymentResponse(**response_data)
    
    # === Error Handling ===
    
    @staticmethod
    def handle_payment_error(status_code: int, error_data: Dict[str, Any]) -> ErrorResponse:
        """
        Handle Payment service errors
        
        Args:
            status_code: HTTP status code
            error_data: Error response data
            
        Returns:
            ErrorResponse: Standardized error response
        """
        return ErrorResponse(
            success=False,
            message=error_data.get("detail", "Payment service error"),
            error_code=f"PAY_{status_code}",
            details=error_data
        )
    
    # === Service Endpoints ===
    
    ENDPOINTS = {
        "create_invoice": "/invoice",
        "webhook_yookassa": "/webhook/yookassa",
        "webhook_stripe": "/webhook/stripe",
        "health": "/",
    }
    
    # === Request Headers ===
    
    @staticmethod
    def get_required_headers() -> Dict[str, str]:
        """
        Get required headers for Payment service requests
        
        Returns:
            Dict[str, str]: Required headers
        """
        from ..auth import get_auth_headers
        return get_auth_headers()
    
    # === Validation Rules ===
    
    VALIDATION_RULES = {
        "min_amount": 1.0,
        "max_amount": 100000.0,
        "supported_currencies": ["RUB", "USD", "EUR"],
        "supported_gateways": ["yookassa", "stripe"],
        "timeout_seconds": 30,
        "max_retries": 3,
    }
    
    # === Payment Plans ===
    
    @staticmethod
    def get_available_plans() -> Dict[str, Dict[str, Any]]:
        """
        Get available payment plans
        
        Returns:
            Dict[str, Dict[str, Any]]: Available payment plans
        """
        from common.config.payment_plans import PAYMENT_PLANS
        return PAYMENT_PLANS