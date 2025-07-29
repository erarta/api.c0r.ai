"""
Migration Guide for c0r.AI ML Service v2.0
Provides utilities and guidance for migrating from v1.0 to v2.0
"""

import json
import warnings
from typing import Dict, Any, Optional, List
from loguru import logger

from .service import MLService


class MigrationHelper:
    """Helper class for migrating from old ML service to new architecture"""
    
    def __init__(self):
        self.new_service = MLService()
        self.migration_log = []
        
        logger.info("🔄 Migration helper initialized")
    
    def migrate_food_analysis_call(self, 
                                  old_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate old food analysis call to new format
        
        Args:
            old_params: Parameters from old API call
            
        Returns:
            Result in new format
        """
        logger.debug("🔄 Migrating food analysis call")
        
        # Map old parameters to new format
        new_params = self._map_old_to_new_params(old_params)
        
        # Log migration
        self.migration_log.append({
            "type": "food_analysis",
            "old_params": old_params,
            "new_params": new_params,
            "timestamp": logger._core.now()
        })
        
        # Call new service
        result = self.new_service.analyze_food(**new_params)
        
        # Convert result to old format if needed
        if old_params.get("legacy_format", False):
            result = self._convert_to_legacy_format(result, "food_analysis")
        
        return result
    
    def migrate_recipe_generation_call(self,
                                     old_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate old recipe generation call to new format
        
        Args:
            old_params: Parameters from old API call
            
        Returns:
            Result in new format
        """
        logger.debug("🔄 Migrating recipe generation call")
        
        # Map parameters
        new_params = self._map_old_to_new_params(old_params)
        
        # Log migration
        self.migration_log.append({
            "type": "recipe_generation",
            "old_params": old_params,
            "new_params": new_params,
            "timestamp": logger._core.now()
        })
        
        # Call new service
        result = self.new_service.generate_recipes(**new_params)
        
        # Convert to legacy format if needed
        if old_params.get("legacy_format", False):
            result = self._convert_to_legacy_format(result, "recipe_generation")
        
        return result
    
    def _map_old_to_new_params(self, old_params: Dict[str, Any]) -> Dict[str, Any]:
        """Map old parameter names to new ones"""
        
        param_mapping = {
            # Old -> New parameter names
            "image": "image_data",
            "lang": "user_language",
            "language": "user_language",
            "user_data": "user_context",
            "context": "user_context",
            "telegram_data": "telegram_user",
            "model_type": "tier"  # Will need conversion
        }
        
        new_params = {}
        
        for old_key, value in old_params.items():
            if old_key in param_mapping:
                new_key = param_mapping[old_key]
                
                # Special handling for model_type -> tier conversion
                if old_key == "model_type":
                    new_params["tier"] = self._convert_model_type_to_tier(value)
                else:
                    new_params[new_key] = value
            else:
                # Keep unknown parameters as-is
                new_params[old_key] = value
        
        return new_params
    
    def _convert_model_type_to_tier(self, old_model_type: str) -> str:
        """Convert old model type to new tier"""
        from .core.models.config.sota_config import ModelTier
        
        conversion_map = {
            "gpt4": ModelTier.SOTA,
            "gpt-4": ModelTier.SOTA,
            "gpt-4o": ModelTier.SOTA,
            "gpt3.5": ModelTier.PREMIUM,
            "gpt-3.5": ModelTier.PREMIUM,
            "gpt-3.5-turbo": ModelTier.PREMIUM,
            "basic": ModelTier.STANDARD,
            "standard": ModelTier.STANDARD,
            "budget": ModelTier.BUDGET
        }
        
        return conversion_map.get(old_model_type, ModelTier.SOTA)
    
    def _convert_to_legacy_format(self, 
                                new_result: Dict[str, Any], 
                                operation_type: str) -> Dict[str, Any]:
        """Convert new result format to legacy format"""
        
        if operation_type == "food_analysis":
            return self._convert_food_analysis_to_legacy(new_result)
        elif operation_type == "recipe_generation":
            return self._convert_recipe_generation_to_legacy(new_result)
        else:
            return new_result
    
    def _convert_food_analysis_to_legacy(self, new_result: Dict[str, Any]) -> Dict[str, Any]:
        """Convert food analysis result to legacy format"""
        
        if not new_result.get("success", False):
            return {
                "status": "error",
                "error": new_result.get("error", "Unknown error"),
                "message": new_result.get("error_details", "")
            }
        
        analysis = new_result.get("analysis", {})
        
        # Legacy format structure
        legacy_result = {
            "status": "success",
            "data": {
                "food_items": analysis.get("food_items", []),
                "total_nutrition": analysis.get("total_nutrition", {}),
                "motivation_message": analysis.get("motivation_message", ""),
                "analysis_time": new_result.get("execution_time", 0)
            },
            "model_info": {
                "model": new_result.get("model_info", {}).get("model_used", ""),
                "tokens": new_result.get("model_info", {}).get("tokens_used", 0)
            }
        }
        
        return legacy_result
    
    def _convert_recipe_generation_to_legacy(self, new_result: Dict[str, Any]) -> Dict[str, Any]:
        """Convert recipe generation result to legacy format"""
        
        if not new_result.get("success", False):
            return {
                "status": "error",
                "error": new_result.get("error", "Unknown error"),
                "message": new_result.get("error_details", "")
            }
        
        recipes = new_result.get("recipes", {})
        
        # Legacy format structure
        legacy_result = {
            "status": "success",
            "data": {
                "recipes": recipes.get("recipes", []),
                "cooking_tips": recipes.get("cooking_tips", []),
                "generation_time": new_result.get("execution_time", 0)
            },
            "model_info": {
                "model": new_result.get("model_info", {}).get("model_used", ""),
                "tokens": new_result.get("model_info", {}).get("tokens_used", 0)
            }
        }
        
        return legacy_result
    
    def get_migration_log(self) -> List[Dict[str, Any]]:
        """Get migration log"""
        return self.migration_log.copy()
    
    def clear_migration_log(self):
        """Clear migration log"""
        self.migration_log.clear()
        logger.info("🗑️ Migration log cleared")


# Backward compatibility wrapper functions
def analyze_food_legacy(image_data: bytes,
                       language: str = "ru",
                       user_data: Dict[str, Any] = None,
                       model_type: str = "gpt4",
                       legacy_format: bool = True) -> Dict[str, Any]:
    """
    Legacy food analysis function for backward compatibility
    
    Args:
        image_data: Image data in bytes
        language: User language
        user_data: User data and preferences
        model_type: Model type to use
        legacy_format: Return result in legacy format
        
    Returns:
        Analysis result in legacy or new format
    """
    warnings.warn(
        "analyze_food_legacy is deprecated. Use MLService.analyze_food() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    helper = MigrationHelper()
    
    old_params = {
        "image_data": image_data,
        "language": language,
        "user_data": user_data or {},
        "model_type": model_type,
        "legacy_format": legacy_format
    }
    
    return helper.migrate_food_analysis_call(old_params)


def generate_recipes_legacy(image_data: bytes,
                           language: str = "ru",
                           user_data: Dict[str, Any] = None,
                           model_type: str = "gpt4",
                           legacy_format: bool = True) -> Dict[str, Any]:
    """
    Legacy recipe generation function for backward compatibility
    
    Args:
        image_data: Image data in bytes
        language: User language
        user_data: User data and preferences
        model_type: Model type to use
        legacy_format: Return result in legacy format
        
    Returns:
        Recipe generation result in legacy or new format
    """
    warnings.warn(
        "generate_recipes_legacy is deprecated. Use MLService.generate_recipes() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    helper = MigrationHelper()
    
    old_params = {
        "image_data": image_data,
        "language": language,
        "user_data": user_data or {},
        "model_type": model_type,
        "legacy_format": legacy_format
    }
    
    return helper.migrate_recipe_generation_call(old_params)


# Migration validation functions
def validate_migration_compatibility() -> Dict[str, Any]:
    """
    Validate that the new service is compatible with old API calls
    
    Returns:
        Validation results
    """
    logger.info("🔍 Validating migration compatibility")
    
    validation_results = {
        "compatible": True,
        "issues": [],
        "warnings": [],
        "recommendations": []
    }
    
    try:
        # Test service initialization
        service = MLService()
        health = service.get_health_status()
        
        if health["service"]["status"] != "healthy":
            validation_results["issues"].append(
                f"Service health status is {health['service']['status']}"
            )
            validation_results["compatible"] = False
        
        # Test migration helper
        helper = MigrationHelper()
        
        # Test parameter mapping
        test_old_params = {
            "image": b"test_data",
            "lang": "ru",
            "user_data": {"goal": "test"},
            "model_type": "gpt4"
        }
        
        new_params = helper._map_old_to_new_params(test_old_params)
        
        expected_keys = ["image_data", "user_language", "user_context", "tier"]
        for key in expected_keys:
            if key not in new_params:
                validation_results["issues"].append(f"Parameter mapping missing: {key}")
                validation_results["compatible"] = False
        
        # Add recommendations
        validation_results["recommendations"].extend([
            "Update client code to use new MLService class directly",
            "Replace legacy function calls with new service methods",
            "Update parameter names to match new API",
            "Consider using new features like regional adaptation"
        ])
        
        if validation_results["compatible"]:
            logger.info("✅ Migration compatibility validation passed")
        else:
            logger.warning("⚠️ Migration compatibility issues found")
        
    except Exception as e:
        validation_results["compatible"] = False
        validation_results["issues"].append(f"Validation error: {str(e)}")
        logger.error(f"❌ Migration validation failed: {e}")
    
    return validation_results


def generate_migration_report() -> str:
    """
    Generate a comprehensive migration report
    
    Returns:
        Migration report as formatted string
    """
    logger.info("📋 Generating migration report")
    
    validation = validate_migration_compatibility()
    
    report = f"""
# c0r.AI ML Service v2.0 Migration Report

## Compatibility Status
**Status**: {'✅ Compatible' if validation['compatible'] else '❌ Issues Found'}

## Service Health
"""
    
    try:
        service = MLService()
        health = service.get_health_status()
        
        report += f"""
- Service Status: {health['service']['status']}
- Version: {health['service']['version']}
- Uptime: {health['service']['uptime_seconds']} seconds
- Success Rate: {health['service']['success_rate']}%
"""
    except Exception as e:
        report += f"- Error getting service health: {e}\n"
    
    if validation['issues']:
        report += "\n## Issues Found\n"
        for issue in validation['issues']:
            report += f"- ❌ {issue}\n"
    
    if validation['warnings']:
        report += "\n## Warnings\n"
        for warning in validation['warnings']:
            report += f"- ⚠️ {warning}\n"
    
    if validation['recommendations']:
        report += "\n## Recommendations\n"
        for rec in validation['recommendations']:
            report += f"- 💡 {rec}\n"
    
    report += """
## Migration Steps

### 1. Update Imports
```python
# Old
from services.ml.old_service import analyze_food, generate_recipes

# New
from services.ml import MLService, analyze_food_image, generate_recipes_from_image
```

### 2. Update Function Calls
```python
# Old
result = analyze_food(image_data, lang="ru", user_data=context)

# New - Option 1 (Direct service)
service = MLService()
result = service.analyze_food(image_data, user_language="ru", user_context=context)

# New - Option 2 (Backward compatible)
result = analyze_food_image(image_data, user_language="ru", user_context=context)
```

### 3. Update Parameter Names
- `image` → `image_data`
- `lang`/`language` → `user_language`
- `user_data` → `user_context`
- `model_type` → `tier`

### 4. Handle New Response Format
The new service provides more detailed responses with metadata, health info, and regional context.

### 5. Leverage New Features
- Regional adaptation based on user location
- Enhanced reliability with fallback mechanisms
- Improved health monitoring and metrics
- Better error handling and logging

## Testing Migration
Use the migration helper to test compatibility:

```python
from services.ml.migration_guide import MigrationHelper

helper = MigrationHelper()
result = helper.migrate_food_analysis_call(old_params)
```
"""
    
    logger.info("📋 Migration report generated")
    return report


# Global migration helper instance
_migration_helper = None

def get_migration_helper() -> MigrationHelper:
    """Get singleton migration helper instance"""
    global _migration_helper
    
    if _migration_helper is None:
        _migration_helper = MigrationHelper()
    
    return _migration_helper