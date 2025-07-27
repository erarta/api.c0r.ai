"""
Configuration settings for c0r.ai API
"""
import os
import sys
from typing import Optional

# Add common directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'common'))

from common.config.payment_plans import get_payment_plans, PAYMENT_PLANS

# Application Version
VERSION = "0.3.19"

# System information
SYSTEM_NAME = "c0r.ai"
SYSTEM_DESCRIPTION = "AI-powered nutrition analysis bot"

# Payment Configuration - Imported from centralized config
# This ensures consistency across all services
# Prices automatically adjust based on ENVIRONMENT and TEST_MODE variables