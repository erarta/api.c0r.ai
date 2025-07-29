"""
Enhanced Prompts System for c0r.AI ML Service
Provides regional adaptation, motivation, and triple recipe generation
"""

from .base.prompt_builder import PromptBuilder
from .motivation.praise_system import MotivationSystem
from .utils.plate_weight_estimator import PlateWeightEstimator
from .nutrition.benefits_explainer import NutritionBenefitsExplainer
from .recipes.triple_generator import TripleRecipeGenerator

__all__ = [
    "PromptBuilder",
    "MotivationSystem", 
    "PlateWeightEstimator",
    "NutritionBenefitsExplainer",
    "TripleRecipeGenerator"
]

# Version info
__version__ = "1.0.0"
__author__ = "c0r.AI Development Team"
__description__ = "Enhanced prompts system with regional adaptation and motivation"