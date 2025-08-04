"""
Payment-related Pydantic models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from .common import BaseResponse


class PaymentPlan(BaseModel):
    """Payment plan model"""
    id: str = Field(..., description="Plan identifier")
    name: str = Field(..., description="Plan display name")
    price: float = Field(..., ge=0, description="Plan price")
    credits: int = Field(..., ge=1, description="Number of credits")
    currency: str = Field(default="RUB", description="Currency code")
    description: Optional[str] = Field(None, description="Plan description")


class InvoiceRequest(BaseModel):
    """Request model for creating payment invoice"""
    user_id: str = Field(..., description="User ID (telegram_id as string)")
    amount: float = Field(..., gt=0, description="Payment amount")
    description: str = Field(..., min_length=1, max_length=200, description="Payment description")
    plan_id: str = Field(default="basic", description="Payment plan identifier")
    currency: str = Field(default="RUB", description="Currency code")
    return_url: Optional[str] = Field(None, description="Return URL after payment")
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)


class InvoiceResponse(BaseResponse):
    """Response model for payment invoice creation"""
    invoice_id: str = Field(..., description="Invoice/payment ID")
    payment_url: str = Field(..., description="URL for payment")
    amount: float = Field(..., description="Payment amount")
    currency: str = Field(..., description="Currency code")
    expires_at: Optional[datetime] = Field(None, description="Invoice expiration time")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional payment metadata")


class PaymentRequest(BaseModel):
    """Request model for payment processing"""
    user_id: str = Field(..., description="User ID")
    payment_id: str = Field(..., description="Payment ID from gateway")
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="RUB", description="Currency code")
    gateway: str = Field(..., pattern="^(yookassa|stripe)$", description="Payment gateway")
    status: str = Field(..., description="Payment status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Payment metadata")


class PaymentResponse(BaseResponse):
    """Response model for payment processing"""
    payment_id: str = Field(..., description="Payment ID")
    status: str = Field(..., description="Payment status")
    amount: float = Field(..., description="Payment amount")
    credits_added: Optional[int] = Field(None, description="Credits added to user account")


class WebhookPayload(BaseModel):
    """Base webhook payload model"""
    event: str = Field(..., description="Webhook event type")
    object: Dict[str, Any] = Field(..., description="Payment object data")
    created_at: Optional[datetime] = Field(None, description="Event creation time")


class YooKassaWebhook(WebhookPayload):
    """YooKassa webhook payload model"""
    pass


class StripeWebhook(WebhookPayload):
    """Stripe webhook payload model"""
    pass


class PaymentVerificationRequest(BaseModel):
    """Request model for payment verification"""
    payment_id: str = Field(..., description="Payment ID to verify")
    gateway: str = Field(..., pattern="^(yookassa|stripe)$", description="Payment gateway")


class PaymentVerificationResponse(BaseResponse):
    """Response model for payment verification"""
    payment_id: str = Field(..., description="Payment ID")
    status: str = Field(..., description="Verified payment status")
    amount: float = Field(..., description="Payment amount")
    verified: bool = Field(..., description="Whether payment is verified")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional verification details")