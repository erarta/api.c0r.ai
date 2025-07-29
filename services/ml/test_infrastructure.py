"""
Test script for basic ML infrastructure
Quick validation of the new architecture components
"""

import sys
import os
import asyncio
from loguru import logger

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

async def test_infrastructure():
    """Test basic infrastructure components"""
    
    logger.info("🧪 Testing ML Infrastructure...")
    
    try:
        # Test 1: Import core modules
        logger.info("📦 Testing imports...")
        
        from services.ml.core.models.config import (
            ModelTier, TaskType, ModelConfig, get_model_config, EnvironmentConfig
        )
        from services.ml.core.models.providers import BaseAIProvider, ModelResponse, OpenAIProvider
        from services.ml.core.models.managers import ModelManager
        
        logger.info("✅ All imports successful")
        
        # Test 2: Configuration validation
        logger.info("⚙️ Testing configuration...")
        
        validation_result = EnvironmentConfig.validate_configuration()
        logger.info(f"Configuration validation: {'✅ Valid' if validation_result['valid'] else '❌ Invalid'}")
        
        if validation_result['errors']:
            for error in validation_result['errors']:
                logger.error(f"  - {error}")
        
        if validation_result['warnings']:
            for warning in validation_result['warnings']:
                logger.warning(f"  - {warning}")
        
        # Test 3: Model configuration
        logger.info("🤖 Testing model configuration...")
        
        try:
            food_analysis_config = get_model_config(TaskType.FOOD_ANALYSIS, ModelTier.SOTA)
            logger.info(f"✅ Food analysis config: {food_analysis_config.name} ({food_analysis_config.provider})")
            
            recipe_config = get_model_config(TaskType.RECIPE_GENERATION, ModelTier.SOTA)
            logger.info(f"✅ Recipe generation config: {recipe_config.name} ({recipe_config.provider})")
            
        except Exception as e:
            logger.error(f"❌ Model configuration error: {e}")
        
        # Test 4: Model Manager initialization
        logger.info("🎯 Testing Model Manager...")
        
        try:
            model_manager = ModelManager()
            
            if model_manager.is_initialized():
                logger.info("✅ Model Manager initialized successfully")
                
                # Get available providers
                providers = model_manager.get_available_providers()
                logger.info(f"📋 Available providers: {len(providers)}")
                
                for provider_key, provider_info in providers.items():
                    logger.info(f"  - {provider_key}: {provider_info['model']} ({provider_info['provider']})")
                
                # Test health check if OpenAI key is available
                if EnvironmentConfig.OPENAI_API_KEY:
                    logger.info("🏥 Running health check...")
                    health_result = await model_manager.health_check()
                    
                    healthy_count = health_result['healthy_providers']
                    total_count = health_result['total_providers']
                    
                    logger.info(f"Health check: {healthy_count}/{total_count} providers healthy")
                    
                    if not health_result['overall_healthy']:
                        logger.warning("⚠️ Some providers are unhealthy")
                        for provider_key, provider_health in health_result['providers'].items():
                            if not provider_health['healthy']:
                                logger.warning(f"  - {provider_key}: {provider_health.get('error', 'Unknown error')}")
                else:
                    logger.warning("⚠️ OpenAI API key not configured, skipping health check")
                
            else:
                logger.error("❌ Model Manager failed to initialize")
                
        except Exception as e:
            logger.error(f"❌ Model Manager error: {e}")
        
        # Test 5: Environment configuration logging
        logger.info("📊 Configuration status:")
        EnvironmentConfig.log_configuration_status()
        
        logger.info("🎉 Infrastructure test completed!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Infrastructure test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    # Set up logging
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )
    
    # Run the test
    success = asyncio.run(test_infrastructure())
    
    if success:
        logger.info("✅ All infrastructure tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Infrastructure tests failed!")
        sys.exit(1)