"""
Model configuration package for c0r.AI ML Service
"""

from .sota_config import (
    ModelTier,
    TaskType,
    ModelConfig,
    SOTA_MODEL_CONFIGS,
    get_model_config,
    get_available_tiers,
    validate_model_config
)

from .environment_config import EnvironmentConfig

__all__ = [
    'ModelTier',
    'TaskType', 
    'ModelConfig',
    'SOTA_MODEL_CONFIGS',
    'get_model_config',
    'get_available_tiers',
    'validate_model_config',
    'EnvironmentConfig'
]