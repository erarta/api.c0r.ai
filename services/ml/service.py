"""
Main ML Service Class for c0r.AI
Integrates all components into a unified service interface
"""

import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import asdict
from loguru import logger

from .core.models.managers.model_manager import ModelManager
from .core.models.config.sota_config import ModelTier, TaskType
from .modules.location.detector import UserLocationDetector
from .core.prompts.base.prompt_builder import PromptBuilder
from .core.reliability.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from .core.reliability.fallback_manager import FallbackManager, FallbackStrategy
from .core.reliability.health_monitor import HealthMonitor, HealthCheckConfig


class MLService:
    """
    Main ML Service class that orchestrates all components
    
    Provides a unified interface for:
    - Food analysis with regional adaptation
    - Recipe generation with cultural context
    - Location-aware processing
    - Reliability and fallback mechanisms
    - Health monitoring and metrics
    """
    
    def __init__(self):
        """Initialize ML Service with all components"""
        logger.info("🚀 Initializing c0r.AI ML Service v2.0")
        
        # Initialize core components
        self.model_manager = ModelManager()
        self.location_detector = UserLocationDetector()
        self.prompt_builder = PromptBuilder()
        
        # Initialize reliability components
        self._setup_reliability()
        
        # Initialize health monitoring
        self._setup_health_monitoring()
        
        # Service statistics
        self.stats = {
            "service_start_time": time.time(),
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "food_analyses": 0,
            "recipe_generations": 0,
            "location_detections": 0,
            "fallback_uses": 0
        }
        
        logger.info("✅ ML Service initialized successfully")
    
    async def analyze_food(self,
                    image_data: bytes,
                    user_language: str = "ru",
                    user_context: Dict[str, Any] = None,
                    user_id: Optional[int] = None,
                    telegram_user: Optional[Dict[str, Any]] = None,
                    tier: ModelTier = ModelTier.SOTA) -> Dict[str, Any]:
        """
        Analyze food image with regional adaptation and reliability
        
        Args:
            image_data: Image data in bytes
            user_language: User language code
            user_context: User context and preferences
            user_id: User ID for location detection
            telegram_user: Telegram user data
            tier: Model tier to use
            
        Returns:
            Analysis result with regional context and reliability metadata
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        self.stats["food_analyses"] += 1
        
        logger.info(f"🍽️ Starting food analysis for user {user_id} in {user_language}")
        
        try:
            # Step 1: Detect user location and regional context
            location_result = None
            if user_id:
                location_result = await self.location_detector.detect_user_location(
                    telegram_user_id=str(user_id),
                    user_language=user_language,
                    telegram_user=telegram_user
                )
                if location_result:
                    self.stats["location_detections"] += 1
                    logger.debug(f"📍 Location detected: {location_result.location.country_code}")
            
            # Step 2: Build regional prompt
            regional_context = location_result.regional_context if location_result else None
            
            # Use fallback manager for analysis
            analysis_result = await self.food_analysis_fallback.execute(
                image_data=image_data,
                user_language=user_language,
                user_context=user_context or {},
                regional_context=regional_context,
                tier=tier
            )
            
            if not analysis_result.success:
                self.stats["failed_requests"] += 1
                self.stats["fallback_uses"] += 1 if analysis_result.fallback_used else 0
                
                return {
                    "success": False,
                    "error": "Analysis failed after all fallback attempts",
                    "error_details": str(analysis_result.error),
                    "execution_time": time.time() - start_time,
                    "metadata": {
                        "service_version": "2.0.0",
                        "attempts_made": analysis_result.attempts_made,
                        "fallback_used": analysis_result.fallback_used
                    }
                }
            
            # Step 3: Process and enhance result
            model_response = analysis_result.result
            
            # Parse JSON response
            try:
                analysis_data = json.loads(model_response.content)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse analysis JSON: {e}")
                analysis_data = {"error": "Invalid response format"}
            
            # Step 4: Build comprehensive response
            response = {
                "success": True,
                "analysis": analysis_data,
                "model_info": {
                    "model_used": model_response.model_used,
                    "tokens_used": model_response.tokens_used,
                    "cost": model_response.cost,
                    "response_time": model_response.response_time
                },
                "location_info": {
                    "detected": location_result is not None,
                    "country_code": location_result.location.country_code if location_result else None,
                    "region_code": location_result.regional_context.region_code if location_result else None,
                    "confidence": location_result.location.confidence if location_result else 0.0
                },
                "execution_time": time.time() - start_time,
                "metadata": {
                    "service_version": "2.0.0",
                    "tier_used": tier.value,
                    "fallback_used": analysis_result.fallback_used,
                    "attempts_made": analysis_result.attempts_made
                }
            }
            
            self.stats["successful_requests"] += 1
            logger.info(f"✅ Food analysis completed in {response['execution_time']:.2f}s")
            
            return response
            
        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"❌ Food analysis failed: {e}")
            
            return {
                "success": False,
                "error": "Internal service error",
                "error_details": str(e),
                "execution_time": time.time() - start_time,
                "metadata": {
                    "service_version": "2.0.0",
                    "error_type": type(e).__name__
                }
            }
    
    async def generate_recipes(self,
                        image_data: bytes,
                        user_language: str = "ru",
                        user_context: Dict[str, Any] = None,
                        user_id: Optional[int] = None,
                        telegram_user: Optional[Dict[str, Any]] = None,
                        tier: ModelTier = ModelTier.SOTA) -> Dict[str, Any]:
        """
        Generate recipes from food image with regional adaptation
        
        Args:
            image_data: Image data in bytes
            user_language: User language code
            user_context: User context and preferences
            user_id: User ID for location detection
            telegram_user: Telegram user data
            tier: Model tier to use
            
        Returns:
            Recipe generation result with regional context
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        self.stats["recipe_generations"] += 1
        
        logger.info(f"👨‍🍳 Starting recipe generation for user {user_id} in {user_language}")
        
        try:
            # Step 1: Detect location if needed
            location_result = None
            if user_id:
                location_result = await self.location_detector.detect_user_location(
                    telegram_user_id=str(user_id),
                    user_language=user_language,
                    telegram_user=telegram_user
                )
                if location_result:
                    self.stats["location_detections"] += 1
            
            # Step 2: Use fallback manager for recipe generation
            regional_context = location_result.regional_context if location_result else None
            
            recipe_result = await self.recipe_generation_fallback.execute(
                image_data=image_data,
                user_language=user_language,
                user_context=user_context or {},
                regional_context=regional_context,
                tier=tier
            )
            
            if not recipe_result.success:
                self.stats["failed_requests"] += 1
                self.stats["fallback_uses"] += 1 if recipe_result.fallback_used else 0
                
                return {
                    "success": False,
                    "error": "Recipe generation failed after all fallback attempts",
                    "error_details": str(recipe_result.error),
                    "execution_time": time.time() - start_time,
                    "metadata": {
                        "service_version": "2.0.0",
                        "attempts_made": recipe_result.attempts_made,
                        "fallback_used": recipe_result.fallback_used
                    }
                }
            
            # Step 3: Process result
            model_response = recipe_result.result
            
            try:
                recipe_data = json.loads(model_response.content)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Failed to parse recipe JSON: {e}")
                recipe_data = {"error": "Invalid response format"}
            
            # Step 4: Build response
            response = {
                "success": True,
                "recipes": recipe_data,
                "model_info": {
                    "model_used": model_response.model_used,
                    "tokens_used": model_response.tokens_used,
                    "cost": model_response.cost,
                    "response_time": model_response.response_time
                },
                "location_info": {
                    "detected": location_result is not None,
                    "country_code": location_result.location.country_code if location_result else None,
                    "region_code": location_result.regional_context.region_code if location_result else None,
                    "confidence": location_result.location.confidence if location_result else 0.0
                },
                "execution_time": time.time() - start_time,
                "metadata": {
                    "service_version": "2.0.0",
                    "tier_used": tier.value,
                    "fallback_used": recipe_result.fallback_used,
                    "attempts_made": recipe_result.attempts_made
                }
            }
            
            self.stats["successful_requests"] += 1
            logger.info(f"✅ Recipe generation completed in {response['execution_time']:.2f}s")
            
            return response
            
        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"❌ Recipe generation failed: {e}")
            
            return {
                "success": False,
                "error": "Internal service error",
                "error_details": str(e),
                "execution_time": time.time() - start_time,
                "metadata": {
                    "service_version": "2.0.0",
                    "error_type": type(e).__name__
                }
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status of the ML service
        
        Returns:
            Health status with all component information
        """
        logger.debug("🏥 Generating health status report")
        
        # Get component health
        model_health = self.model_manager.get_health_status()
        location_stats = self.location_detector.get_cache_stats()
        
        # Calculate service metrics
        uptime = time.time() - self.stats["service_start_time"]
        success_rate = 0.0
        if self.stats["total_requests"] > 0:
            success_rate = (self.stats["successful_requests"] / self.stats["total_requests"]) * 100
        
        # Get reliability component stats
        fallback_stats = {
            "food_analysis": self.food_analysis_fallback.get_stats(),
            "recipe_generation": self.recipe_generation_fallback.get_stats()
        }
        
        # Get health monitor report
        health_report = self.health_monitor.get_health_report()
        
        return {
            "service": {
                "name": "c0r.AI ML Service",
                "version": "2.0.0",
                "status": "healthy" if success_rate > 90 else "degraded" if success_rate > 50 else "unhealthy",
                "uptime_seconds": int(uptime),
                "success_rate": round(success_rate, 2)
            },
            "statistics": self.stats.copy(),
            "components": {
                "model_manager": model_health,
                "location_detector": location_stats,
                "fallback_managers": fallback_stats
            },
            "health_monitoring": health_report,
            "timestamp": time.time()
        }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get detailed service statistics"""
        return {
            "service_stats": self.stats.copy(),
            "model_manager_stats": self.model_manager.get_health_status(),
            "location_detector_stats": self.location_detector.get_cache_stats(),
            "fallback_stats": {
                "food_analysis": self.food_analysis_fallback.get_stats(),
                "recipe_generation": self.recipe_generation_fallback.get_stats()
            }
        }
    
    def reset_stats(self):
        """Reset service statistics"""
        self.stats = {
            "service_start_time": time.time(),
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "food_analyses": 0,
            "recipe_generations": 0,
            "location_detections": 0,
            "fallback_uses": 0
        }
        
        logger.info("📊 Service statistics reset")
    
    def _setup_reliability(self):
        """Setup reliability components (fallback managers, circuit breakers)"""
        logger.debug("🔧 Setting up reliability components")
        
        # Circuit breaker configurations
        cb_config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=60,
            success_threshold=2,
            timeout=30.0
        )
        
        # Food analysis fallback manager
        self.food_analysis_fallback = FallbackManager(
            "food_analysis", 
            FallbackStrategy.SEQUENTIAL
        )
        
        # Add primary analysis option
        self.food_analysis_fallback.add_option(
            name="primary_analysis",
            func=self._analyze_food_primary,
            weight=1.0,
            circuit_breaker_config=cb_config,
            timeout=30.0,
            retry_count=2
        )
        
        # Add fallback analysis option
        self.food_analysis_fallback.add_option(
            name="fallback_analysis", 
            func=self._analyze_food_fallback,
            weight=0.8,
            timeout=45.0,
            retry_count=1
        )
        
        # Recipe generation fallback manager
        self.recipe_generation_fallback = FallbackManager(
            "recipe_generation",
            FallbackStrategy.SEQUENTIAL
        )
        
        # Add primary recipe option
        self.recipe_generation_fallback.add_option(
            name="primary_recipes",
            func=self._generate_recipes_primary,
            weight=1.0,
            circuit_breaker_config=cb_config,
            timeout=45.0,
            retry_count=2
        )
        
        # Add fallback recipe option
        self.recipe_generation_fallback.add_option(
            name="fallback_recipes",
            func=self._generate_recipes_fallback,
            weight=0.8,
            timeout=60.0,
            retry_count=1
        )
        
        logger.debug("✅ Reliability components configured")
    
    def _setup_health_monitoring(self):
        """Setup health monitoring"""
        logger.debug("🏥 Setting up health monitoring")
        
        self.health_monitor = HealthMonitor("ml_service")
        
        # Add health checks
        self.health_monitor.add_check(HealthCheckConfig(
            name="model_manager",
            check_function=self._check_model_manager_health,
            interval=60,
            critical=True
        ))
        
        self.health_monitor.add_check(HealthCheckConfig(
            name="location_detector",
            check_function=self._check_location_detector_health,
            interval=120,
            critical=False
        ))
        
        # Start monitoring
        self.health_monitor.start_monitoring(30)
        
        logger.debug("✅ Health monitoring configured")
    
    async def _analyze_food_primary(self, **kwargs):
        """Primary food analysis method"""
        return await self.model_manager.analyze_food(**kwargs)
    
    async def _analyze_food_fallback(self, **kwargs):
        """Fallback food analysis method"""
        # Use lower tier model for fallback
        kwargs['tier'] = ModelTier.PREMIUM
        return await self.model_manager.analyze_food(**kwargs)
    
    async def _generate_recipes_primary(self, **kwargs):
        """Primary recipe generation method"""
        return await self.model_manager.generate_recipes(**kwargs)
    
    async def _generate_recipes_fallback(self, **kwargs):
        """Fallback recipe generation method"""
        # Use lower tier model for fallback
        kwargs['tier'] = ModelTier.PREMIUM
        return await self.model_manager.generate_recipes(**kwargs)
    
    def _check_model_manager_health(self):
        """Health check for model manager"""
        from .core.reliability.health_monitor import HealthCheckResult, HealthStatus
        
        try:
            health = self.model_manager.get_health_status()
            
            if health["overall_status"] == "healthy":
                return HealthCheckResult(
                    name="model_manager",
                    status=HealthStatus.HEALTHY,
                    message="Model manager is healthy",
                    details=health
                )
            else:
                return HealthCheckResult(
                    name="model_manager",
                    status=HealthStatus.DEGRADED,
                    message=f"Model manager status: {health['overall_status']}",
                    details=health
                )
                
        except Exception as e:
            return HealthCheckResult(
                name="model_manager",
                status=HealthStatus.UNHEALTHY,
                message=f"Model manager health check failed: {e}",
                error=e
            )
    
    def _check_location_detector_health(self):
        """Health check for location detector"""
        from .core.reliability.health_monitor import HealthCheckResult, HealthStatus
        
        try:
            stats = self.location_detector.get_cache_stats()
            
            # Simple health check based on cache hit rate
            cache_hit_rate = stats.get("cache_hit_rate", 0)
            
            if cache_hit_rate > 0.5:
                status = HealthStatus.HEALTHY
                message = f"Location detector healthy (cache hit rate: {cache_hit_rate:.2f})"
            else:
                status = HealthStatus.DEGRADED
                message = f"Location detector degraded (low cache hit rate: {cache_hit_rate:.2f})"
            
            return HealthCheckResult(
                name="location_detector",
                status=status,
                message=message,
                details=stats
            )
            
        except Exception as e:
            return HealthCheckResult(
                name="location_detector",
                status=HealthStatus.UNHEALTHY,
                message=f"Location detector health check failed: {e}",
                error=e
            )
    
    def __del__(self):
        """Cleanup on service destruction"""
        try:
            if hasattr(self, 'health_monitor'):
                self.health_monitor.stop_monitoring()
            logger.info("🛑 ML Service cleanup completed")
        except:
            pass