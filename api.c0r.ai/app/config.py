"""
Configuration settings for c0r.ai API
"""
import os
from typing import Optional

# Application Version
VERSION = "0.3.15"

# System information
SYSTEM_NAME = "c0r.ai"
SYSTEM_DESCRIPTION = "AI-powered nutrition analysis bot"

# Payment Configuration - Single source of truth
# Set to 99 RUB and 149 RUB for production
PAYMENT_PLANS = {
    "basic": {
        "title": "Basic Plan",
        "description": "20 credits for food analysis",
        "price": 9900,  # 99 RUB in kopecks
        "credits": 20,
        "currency": "RUB",
        "recurring": False
    },
    "pro": {
        "title": "Pro Plan", 
        "description": "100 credits for food analysis",
        "price": 14900,  # 149 RUB in kopecks
        "credits": 100,
        "currency": "RUB",
        "recurring": True,
        "interval": "month"
    }
} 