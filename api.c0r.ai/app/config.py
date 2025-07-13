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
# NOTE: Set to minimum Telegram-accepted amounts for testing (normally 99 and 399 rubles)
PAYMENT_PLANS = {
    "basic": {
        "title": "Basic Plan",
        "description": "20 credits for food analysis",
        "price": 1000,  # 10 RUB in kopecks (minimum Telegram amount for testing, normally 9900)
        "credits": 20,
        "currency": "RUB",
        "recurring": False
    },
    "pro": {
        "title": "Pro Plan", 
        "description": "100 credits for food analysis",
        "price": 5000,  # 50 RUB in kopecks (minimum Telegram amount for testing, normally 39900)
        "credits": 100,
        "currency": "RUB",
        "recurring": True,
        "interval": "month"
    }
} 