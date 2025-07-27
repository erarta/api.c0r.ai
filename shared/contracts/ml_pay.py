"""
ML ↔ Payment Service Contract
Defines the interface between ML service and Payment service (if needed)
"""

from typing import Dict, Any, Optional
from ..models.common import BaseResponse, ErrorResponse


class MLPayContract:
    """Contract for ML service to Payment service communication"""
    
    # Note: Currently ML service doesn't directly communicate with Payment service
    # This contract is reserved for future use cases like:
    # - Premium AI model usage tracking
    # - Usage-based billing
    # - AI model cost allocation
    
    # === Future: Premium Model Usage ===
    
    @staticmethod
    def track_premium_usage_request(
        user_id: str,
        model_used: str,
        tokens_consumed: int,
        processing_time: float,
        cost_estimate: float
    ) -> Dict[str, Any]:
        """
        Create request for tracking premium AI model usage
        
        Args:
            user_id: User ID
            model_used: AI model identifier (e.g., "gpt-4o", "claude-3")
            tokens_consumed: Number of tokens used
            processing_time: Processing time in seconds
            cost_estimate: Estimated cost in USD
            
        Returns:
            Dict[str, Any]: Usage tracking request
        """
        return {
            "user_id": user_id,
            "model_used": model_used,
            "tokens_consumed": tokens_consumed,
            "processing_time": processing_time,
            "cost_estimate": cost_estimate,
            "timestamp": None  # Will be set by the service
        }
    
    # === Future: Usage-Based Billing ===
    
    @staticmethod
    def calculate_usage_cost_request(
        user_id: str,
        usage_period: str,
        model_usage: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Create request for calculating usage-based costs
        
        Args:
            user_id: User ID
            usage_period: Period for calculation (e.g., "monthly", "daily")
            model_usage: Dictionary of model -> usage count
            
        Returns:
            Dict[str, Any]: Cost calculation request
        """
        return {
            "user_id": user_id,
            "usage_period": usage_period,
            "model_usage": model_usage
        }
    
    # === Future: AI Model Cost Allocation ===
    
    @staticmethod
    def allocate_model_costs_request(
        total_cost: float,
        model_distribution: Dict[str, float],
        billing_period: str
    ) -> Dict[str, Any]:
        """
        Create request for allocating AI model costs across users
        
        Args:
            total_cost: Total cost for the period
            model_distribution: Distribution of usage per model
            billing_period: Billing period identifier
            
        Returns:
            Dict[str, Any]: Cost allocation request
        """
        return {
            "total_cost": total_cost,
            "model_distribution": model_distribution,
            "billing_period": billing_period
        }
    
    # === Error Handling ===
    
    @staticmethod
    def handle_payment_error(status_code: int, error_data: Dict[str, Any]) -> ErrorResponse:
        """
        Handle Payment service errors from ML service perspective
        
        Args:
            status_code: HTTP status code
            error_data: Error response data
            
        Returns:
            ErrorResponse: Standardized error response
        """
        return ErrorResponse(
            success=False,
            message=error_data.get("detail", "Payment service error from ML"),
            error_code=f"ML_PAY_{status_code}",
            details=error_data
        )
    
    # === Service Endpoints (Future) ===
    
    ENDPOINTS = {
        "track_usage": "/usage/track",
        "calculate_costs": "/usage/calculate",
        "allocate_costs": "/usage/allocate",
    }
    
    # === Request Headers ===
    
    @staticmethod
    def get_required_headers() -> Dict[str, str]:
        """
        Get required headers for Payment service requests from ML service
        
        Returns:
            Dict[str, str]: Required headers
        """
        from ..auth import get_auth_headers
        return get_auth_headers()
    
    # === Configuration ===
    
    CONFIG = {
        "usage_tracking_enabled": False,  # Feature flag
        "cost_allocation_enabled": False,  # Feature flag
        "billing_integration_enabled": False,  # Feature flag
    }
    
    # === Model Cost Mapping (Future) ===
    
    MODEL_COSTS = {
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},  # per 1K tokens
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    }
    
    @staticmethod
    def calculate_model_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate cost for AI model usage
        
        Args:
            model: Model identifier
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            float: Calculated cost in USD
        """
        if model not in MLPayContract.MODEL_COSTS:
            return 0.0
        
        costs = MLPayContract.MODEL_COSTS[model]
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        return round(input_cost + output_cost, 6)