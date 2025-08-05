"""
Location Providers for c0r.AI ML Service
"""

from .telegram import TelegramLocationProvider
from .ip_geolocation import IPGeolocationProvider

__all__ = [
    'TelegramLocationProvider',
    'IPGeolocationProvider'
]