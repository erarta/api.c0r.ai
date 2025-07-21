"""
Common Pydantic models used across all services
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model for all API responses"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response model"""
    service: str
    status: str = "healthy"
    version: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    dependencies: Optional[Dict[str, str]] = None


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = 1
    per_page: int = 20
    total: int = 0
    pages: int = 0


class PaginatedResponse(BaseResponse):
    """Paginated response model"""
    data: list = []
    meta: PaginationMeta