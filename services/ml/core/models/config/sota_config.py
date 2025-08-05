"""
SOTA Model Configuration for c0r.AI ML Service
Centralized configuration for state-of-the-art models with GPT-4o as primary choice
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
import os


class ModelTier(Enum):
    """Уровни качества моделей"""
    SOTA = "sota"           # Максимальное качество
    PREMIUM = "premium"     # Высокое качество
    STANDARD = "standard"   # Стандартное качество
    BUDGET = "budget"       # Экономичный вариант


class TaskType(Enum):
    """Типы задач ML"""
    FOOD_ANALYSIS = "food_analysis"
    RECIPE_GENERATION = "recipe_generation"
    NUTRITION_EXPLANATION = "nutrition_explanation"
    MOTIVATION_GENERATION = "motivation_generation"


@dataclass
class ModelConfig:
    """Конфигурация модели"""
    name: str
    provider: str
    tier: ModelTier
    max_tokens: int
    temperature: float
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    timeout: int
    retry_attempts: int
    cost_per_1k_tokens: float
    vision_support: bool
    json_mode: bool
    system_prompt_support: bool


# SOTA конфигурация для максимального качества
SOTA_MODEL_CONFIGS = {
    TaskType.FOOD_ANALYSIS: {
        ModelTier.SOTA: ModelConfig(
            name="gpt-4o",
            provider="openai",
            tier=ModelTier.SOTA,
            max_tokens=2000,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            timeout=60,
            retry_attempts=3,
            cost_per_1k_tokens=0.005,
            vision_support=True,
            json_mode=True,
            system_prompt_support=True
        ),
        ModelTier.PREMIUM: ModelConfig(
            name="gpt-4o-mini",
            provider="openai",
            tier=ModelTier.PREMIUM,
            max_tokens=1500,
            temperature=0.1,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            timeout=45,
            retry_attempts=3,
            cost_per_1k_tokens=0.00015,
            vision_support=True,
            json_mode=True,
            system_prompt_support=True
        ),
        ModelTier.STANDARD: ModelConfig(
            name="claude-4.0",
            provider="anthropic",
            tier=ModelTier.STANDARD,
            max_tokens=1500,
            temperature=0.1,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            timeout=45,
            retry_attempts=2,
            cost_per_1k_tokens=0.003,
            vision_support=True,
            json_mode=False,
            system_prompt_support=True
        )
    },
    
    TaskType.RECIPE_GENERATION: {
        ModelTier.SOTA: ModelConfig(
            name="gpt-4o",
            provider="openai",
            tier=ModelTier.SOTA,
            max_tokens=3000,
            temperature=0.3,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            timeout=90,
            retry_attempts=3,
            cost_per_1k_tokens=0.005,
            vision_support=True,
            json_mode=True,
            system_prompt_support=True
        ),
        ModelTier.PREMIUM: ModelConfig(
            name="claude-4.0",
            provider="anthropic",
            tier=ModelTier.PREMIUM,
            max_tokens=2500,
            temperature=0.3,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            timeout=75,
            retry_attempts=2,
            cost_per_1k_tokens=0.003,
            vision_support=True,
            json_mode=False,
            system_prompt_support=True
        ),
        ModelTier.STANDARD: ModelConfig(
            name="gpt-4o-mini",
            provider="openai",
            tier=ModelTier.STANDARD,
            max_tokens=2000,
            temperature=0.3,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            timeout=60,
            retry_attempts=2,
            cost_per_1k_tokens=0.00015,
            vision_support=True,
            json_mode=True,
            system_prompt_support=True
        )
    },
    
    TaskType.NUTRITION_EXPLANATION: {
        ModelTier.SOTA: ModelConfig(
            name="gpt-4o",
            provider="openai",
            tier=ModelTier.SOTA,
            max_tokens=1000,
            temperature=0.2,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            timeout=45,
            retry_attempts=3,
            cost_per_1k_tokens=0.005,
            vision_support=False,
            json_mode=True,
            system_prompt_support=True
        ),
        ModelTier.PREMIUM: ModelConfig(
            name="gpt-4o-mini",
            provider="openai",
            tier=ModelTier.PREMIUM,
            max_tokens=800,
            temperature=0.2,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            timeout=30,
            retry_attempts=2,
            cost_per_1k_tokens=0.00015,
            vision_support=False,
            json_mode=True,
            system_prompt_support=True
        )
    },
    
    TaskType.MOTIVATION_GENERATION: {
        ModelTier.SOTA: ModelConfig(
            name="gpt-4o",
            provider="openai",
            tier=ModelTier.SOTA,
            max_tokens=500,
            temperature=0.4,
            top_p=0.9,
            frequency_penalty=0.2,
            presence_penalty=0.1,
            timeout=30,
            retry_attempts=2,
            cost_per_1k_tokens=0.005,
            vision_support=False,
            json_mode=False,
            system_prompt_support=True
        ),
        ModelTier.PREMIUM: ModelConfig(
            name="gpt-4o-mini",
            provider="openai",
            tier=ModelTier.PREMIUM,
            max_tokens=400,
            temperature=0.4,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.1,
            timeout=25,
            retry_attempts=2,
            cost_per_1k_tokens=0.00015,
            vision_support=False,
            json_mode=False,
            system_prompt_support=True
        )
    }
}


def get_model_config(task_type: TaskType, tier: ModelTier = ModelTier.SOTA) -> ModelConfig:
    """
    Получить конфигурацию модели для задачи
    
    Args:
        task_type: Тип задачи
        tier: Уровень модели
        
    Returns:
        Конфигурация модели
        
    Raises:
        ValueError: Если конфигурация не найдена
    """
    if task_type not in SOTA_MODEL_CONFIGS:
        raise ValueError(f"Unknown task type: {task_type}")
    
    task_configs = SOTA_MODEL_CONFIGS[task_type]
    if tier not in task_configs:
        # Fallback на доступный tier
        available_tiers = list(task_configs.keys())
        if available_tiers:
            tier = available_tiers[0]
        else:
            raise ValueError(f"No configurations available for task: {task_type}")
    
    return task_configs[tier]


def get_available_tiers(task_type: TaskType) -> List[ModelTier]:
    """
    Получить доступные уровни моделей для задачи
    
    Args:
        task_type: Тип задачи
        
    Returns:
        Список доступных уровней
    """
    if task_type not in SOTA_MODEL_CONFIGS:
        return []
    
    return list(SOTA_MODEL_CONFIGS[task_type].keys())


def validate_model_config(config: ModelConfig) -> bool:
    """
    Валидация конфигурации модели
    
    Args:
        config: Конфигурация для проверки
        
    Returns:
        True если конфигурация валидна
    """
    required_fields = [
        'name', 'provider', 'tier', 'max_tokens', 'temperature',
        'timeout', 'retry_attempts', 'cost_per_1k_tokens'
    ]
    
    for field in required_fields:
        if not hasattr(config, field):
            return False
        
        value = getattr(config, field)
        if value is None:
            return False
    
    # Проверка диапазонов значений
    if not (0.0 <= config.temperature <= 2.0):
        return False
    
    if not (0.0 <= config.top_p <= 1.0):
        return False
    
    if config.max_tokens <= 0:
        return False
    
    if config.timeout <= 0:
        return False
    
    if config.retry_attempts < 0:
        return False
    
    return True