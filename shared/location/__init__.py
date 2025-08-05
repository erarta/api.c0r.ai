"""
Shared Location Module for c0r.AI
Location detection and regional context functionality
"""

from .models import (
    LocationInfo,
    RegionalContext,
    LocationResult,
    DetectionSource,
    DetectionConfidence
)
from .detector import LocationDetector
from .regional_data import (
    get_regional_cuisine,
    get_default_cuisine,
    get_available_regions,
    search_products_by_region,
    get_seasonal_products,
    get_cooking_methods,
    is_product_common_in_region,
    REGIONAL_CUISINES
)

__version__ = "1.0.0"

__all__ = [
    # Models
    'LocationInfo',
    'RegionalContext', 
    'LocationResult',
    'DetectionSource',
    'DetectionConfidence',
    
    # Main detector
    'LocationDetector',
    
    # Regional data functions
    'get_regional_cuisine',
    'get_default_cuisine',
    'get_available_regions',
    'search_products_by_region',
    'get_seasonal_products',
    'get_cooking_methods',
    'is_product_common_in_region',
    'REGIONAL_CUISINES'
]