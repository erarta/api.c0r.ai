"""
Configuration settings for c0r.ai API
"""
import os
from typing import Optional

# Application Version
VERSION = "0.3.14"

# System information
SYSTEM_NAME = "c0r.ai"
SYSTEM_DESCRIPTION = "AI-powered nutrition analysis bot"

# Payment Configuration - Single source of truth
# NOTE: Temporarily set to 1 and 5 rubles for testing (normally 99 and 399 rubles)
PAYMENT_PLANS = {
    "basic": {
        "title": "Basic Plan",
        "description": "20 credits for food analysis",
        "price": 100,  # 1 RUB in kopecks (temporarily for testing, normally 9900)
        "credits": 20,
        "currency": "RUB",
        "recurring": False
    },
    "pro": {
        "title": "Pro Plan", 
        "description": "100 credits for food analysis",
        "price": 500,  # 5 RUB in kopecks (temporarily for testing, normally 39900)
        "credits": 100,
        "currency": "RUB",
        "recurring": True,
        "interval": "month"
    }
} 