"""
OpenAI Model Configuration for ML Service
Centralized settings for food analysis and recipe generation
"""

import os
from typing import Dict, Any

# Default model configurations
DEFAULT_ANALYSIS_MODEL = "gpt-4o"
DEFAULT_RECIPE_MODEL = "gpt-4o"

# Model configurations for different tasks
MODEL_CONFIGS = {
    "analysis": {
        "model": os.getenv("OPENAI_ANALYSIS_MODEL", DEFAULT_ANALYSIS_MODEL),
        "max_tokens": int(os.getenv("OPENAI_ANALYSIS_MAX_TOKENS", "1000")),  # Increased from 500 to 1000
        "temperature": float(os.getenv("OPENAI_ANALYSIS_TEMPERATURE", "0.05")),  # Decreased from 0.1 to 0.05 for more precision
        "fallback_model": os.getenv("OPENAI_ANALYSIS_FALLBACK_MODEL", "gpt-4o-mini")
    },
    "recipe": {
        "model": os.getenv("OPENAI_RECIPE_MODEL", DEFAULT_RECIPE_MODEL),
        "max_tokens": int(os.getenv("OPENAI_RECIPE_MAX_TOKENS", "1000")),
        "temperature": float(os.getenv("OPENAI_RECIPE_TEMPERATURE", "0.3")),
        "fallback_model": os.getenv("OPENAI_RECIPE_FALLBACK_MODEL", "gpt-4o-mini")
    }
}

# Available models for different tiers
AVAILABLE_MODELS = {
    "premium": ["gpt-4o", "gpt-4o-mini"],
    "standard": ["gpt-4o-mini", "gpt-4o"],
    "budget": ["gpt-4o-mini"]
}

def get_model_config(task: str, use_premium: bool = False) -> Dict[str, Any]:
    """
    Get model configuration for specific task
    
    Args:
        task: 'analysis' or 'recipe'
        use_premium: Whether to use premium model settings
        
    Returns:
        Dictionary with model configuration
    """
    if task not in MODEL_CONFIGS:
        raise ValueError(f"Unknown task: {task}")
    
    config = MODEL_CONFIGS[task].copy()
    
    # Override with premium settings if requested
    if use_premium:
        config["model"] = "gpt-4o"
        config["max_tokens"] = max(config["max_tokens"], 800)
    
    return config

def get_available_models_for_tier(tier: str) -> list:
    """
    Get available models for user tier
    
    Args:
        tier: 'premium', 'standard', or 'budget'
        
    Returns:
        List of available model names
    """
    return AVAILABLE_MODELS.get(tier, AVAILABLE_MODELS["standard"])

def validate_model_for_task(model: str, task: str) -> bool:
    """
    Validate if model is suitable for specific task
    
    Args:
        model: Model name to validate
        task: Task type ('analysis' or 'recipe')
        
    Returns:
        True if model is valid for task
    """
    if task == "analysis":
        return model in ["gpt-4o", "gpt-4o-mini", "gpt-4"]
    elif task == "recipe":
        return model in ["gpt-4o", "gpt-4o-mini", "gpt-4"]
    return False

# Environment variable documentation
ENV_VARS = {
    "OPENAI_ANALYSIS_MODEL": "Model for food analysis (default: gpt-4o)",
    "OPENAI_ANALYSIS_MAX_TOKENS": "Max tokens for analysis (default: 500)",
    "OPENAI_ANALYSIS_TEMPERATURE": "Temperature for analysis (default: 0.1)",
    "OPENAI_RECIPE_MODEL": "Model for recipe generation (default: gpt-4o)",
    "OPENAI_RECIPE_MAX_TOKENS": "Max tokens for recipes (default: 1000)",
    "OPENAI_RECIPE_TEMPERATURE": "Temperature for recipes (default: 0.3)"
} 