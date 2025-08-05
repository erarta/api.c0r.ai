"""
Regional Data for c0r.AI ML Service
"""

from .cuisines import (
    get_regional_cuisine,
    get_default_cuisine,
    get_available_regions,
    search_products_by_region,
    get_seasonal_products,
    get_cooking_methods,
    is_product_common_in_region,
    REGIONAL_CUISINES
)

__all__ = [
    'get_regional_cuisine',
    'get_default_cuisine',
    'get_available_regions',
    'search_products_by_region',
    'get_seasonal_products',
    'get_cooking_methods',
    'is_product_common_in_region',
    'REGIONAL_CUISINES'
]