"""
User Location Detector for c0r.AI ML Service
Main location detection system with multiple providers and fallback strategies
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

from .models import (
    LocationInfo, RegionalContext, LocationDetectionResult, LocationCache,
    DetectionMethod, DetectionConfidence
)
from .providers.telegram import TelegramLocationProvider
from .providers.ip_geolocation import IPGeolocationProvider
from .regional_data.cuisines import get_regional_cuisine, get_default_cuisine
from ...core.models.config.environment_config import EnvironmentConfig


class UserLocationDetector:
    """Основной класс для определения локации пользователя"""
    
    def __init__(self):
        # Инициализация провайдеров
        self.telegram_provider = TelegramLocationProvider()
        self.ip_provider = IPGeolocationProvider()
        
        # Кэш локаций пользователей
        self.location_cache: Dict[str, LocationCache] = {}
        
        # Настройки кэширования
        self.cache_ttl = timedelta(seconds=EnvironmentConfig.LOCATION_CACHE_TTL)
        
        # Fallback цепочка
        self.detection_chain = [
            self._detect_via_telegram,
            self._detect_via_ip,
            self._detect_via_timezone,
            self._detect_via_language_fallback
        ]
        
        logger.info("🌍 UserLocationDetector initialized")
    
    async def detect_user_location(self, 
                                 telegram_user_id: str, 
                                 user_language: str,
                                 ip_address: Optional[str] = None,
                                 timezone: Optional[str] = None,
                                 request_headers: Optional[Dict[str, str]] = None) -> LocationDetectionResult:
        """
        Определяет локацию пользователя используя несколько методов
        
        Args:
            telegram_user_id: ID пользователя в Telegram
            user_language: Язык пользователя
            ip_address: IP адрес (опционально)
            timezone: Временная зона (опционально)
            request_headers: Заголовки HTTP запроса (опционально)
            
        Returns:
            LocationDetectionResult с информацией о локации
        """
        logger.info(f"🔍 Detecting location for user {telegram_user_id}")
        
        try:
            # Проверяем кэш
            cached_location = self._get_cached_location(telegram_user_id)
            if cached_location:
                logger.info(f"✅ Using cached location for user {telegram_user_id}: {cached_location.location_info.country_code}")
                return LocationDetectionResult(
                    location=cached_location.location_info,
                    regional_context=cached_location.regional_context,
                    success=True,
                    cache_hit=True
                )
            
            # Подготавливаем контекст для детекции
            detection_context = {
                "telegram_user_id": telegram_user_id,
                "user_language": user_language,
                "ip_address": ip_address,
                "timezone": timezone,
                "request_headers": request_headers or {}
            }
            
            # Если IP не предоставлен, пытаемся извлечь из заголовков
            if not ip_address and request_headers:
                ip_address = await self.ip_provider.get_client_ip_from_request(request_headers)
                detection_context["ip_address"] = ip_address
            
            # Пробуем методы детекции по порядку
            for detection_method in self.detection_chain:
                try:
                    location = await detection_method(detection_context)
                    if location:
                        # Получаем региональный контекст
                        regional_context = self.get_regional_cuisine_context(location)
                        
                        # Кэшируем результат
                        await self._cache_location(telegram_user_id, location, regional_context)
                        
                        logger.info(f"✅ Location detected for user {telegram_user_id}: {location.country_code} via {location.detection_method}")
                        
                        return LocationDetectionResult(
                            location=location,
                            regional_context=regional_context,
                            success=True,
                            fallback_used=location.detection_method != DetectionMethod.TELEGRAM_API
                        )
                        
                except Exception as e:
                    logger.warning(f"⚠️ Detection method {detection_method.__name__} failed: {e}")
                    continue
            
            # Все методы не сработали - используем fallback по умолчанию
            logger.warning(f"❌ All detection methods failed for user {telegram_user_id}, using default")
            
            default_location = self._get_default_location(user_language)
            default_context = self.get_regional_cuisine_context(default_location)
            
            return LocationDetectionResult(
                location=default_location,
                regional_context=default_context,
                success=True,
                fallback_used=True
            )
            
        except Exception as e:
            logger.error(f"❌ Location detection error for user {telegram_user_id}: {e}")
            
            # Критическая ошибка - возвращаем default
            default_location = self._get_default_location(user_language)
            default_context = self.get_regional_cuisine_context(default_location)
            
            return LocationDetectionResult(
                location=default_location,
                regional_context=default_context,
                success=False,
                error_message=str(e),
                fallback_used=True
            )
    
    async def _detect_via_telegram(self, context: Dict[str, Any]) -> Optional[LocationInfo]:
        """Определение через Telegram API"""
        if not self.telegram_provider.is_configured():
            logger.debug("🤖 Telegram provider not configured")
            return None
        
        telegram_user_id = context["telegram_user_id"]
        return await self.telegram_provider.get_location(telegram_user_id)
    
    async def _detect_via_ip(self, context: Dict[str, Any]) -> Optional[LocationInfo]:
        """Определение через IP геолокацию"""
        ip_address = context.get("ip_address")
        if not ip_address:
            logger.debug("🌐 No IP address provided for geolocation")
            return None
        
        return await self.ip_provider.get_location(ip_address)
    
    async def _detect_via_timezone(self, context: Dict[str, Any]) -> Optional[LocationInfo]:
        """Определение по временной зоне"""
        timezone = context.get("timezone")
        if not timezone:
            logger.debug("🕐 No timezone provided")
            return None
        
        # Маппинг timezone на регионы
        timezone_mapping = {
            "Europe/Moscow": ("RU", "Russia", "Moscow"),
            "Europe/Berlin": ("DE", "Germany", "Berlin"),
            "America/New_York": ("US", "United States", "New York"),
            "America/Los_Angeles": ("US", "United States", "California"),
            "Europe/Paris": ("FR", "France", "Paris"),
            "Europe/Rome": ("IT", "Italy", "Rome"),
            "Asia/Tokyo": ("JP", "Japan", "Tokyo"),
            "Europe/London": ("GB", "United Kingdom", "London"),
        }
        
        if timezone in timezone_mapping:
            country_code, country_name, region = timezone_mapping[timezone]
            
            logger.debug(f"🕐 Location detected via timezone {timezone}: {country_code}")
            
            return LocationInfo(
                country_code=country_code,
                country_name=country_name,
                region=region,
                city=None,
                timezone=timezone,
                latitude=None,
                longitude=None,
                confidence=DetectionConfidence.LOW,
                detection_method=DetectionMethod.TIMEZONE_MAPPING
            )
        
        logger.debug(f"🕐 Unknown timezone: {timezone}")
        return None
    
    async def _detect_via_language_fallback(self, context: Dict[str, Any]) -> Optional[LocationInfo]:
        """Fallback определение по языку пользователя"""
        user_language = context["user_language"]
        
        # Маппинг языков на страны (очень приблизительный)
        language_mapping = {
            "ru": ("RU", "Russia", "Central Russia"),
            "en": ("US", "United States", "North America"),
            "de": ("DE", "Germany", "Central Europe"),
            "fr": ("FR", "France", "Western Europe"),
            "it": ("IT", "Italy", "Southern Europe"),
            "ja": ("JP", "Japan", "East Asia"),
            "es": ("ES", "Spain", "Southern Europe"),
            "pt": ("BR", "Brazil", "South America"),
            "zh": ("CN", "China", "East Asia"),
        }
        
        if user_language in language_mapping:
            country_code, country_name, region = language_mapping[user_language]
            
            logger.debug(f"🗣️ Location fallback via language {user_language}: {country_code}")
            
            return LocationInfo(
                country_code=country_code,
                country_name=country_name,
                region=region,
                city=None,
                timezone=None,
                latitude=None,
                longitude=None,
                confidence=DetectionConfidence.VERY_LOW,
                detection_method=DetectionMethod.LANGUAGE_FALLBACK
            )
        
        logger.debug(f"🗣️ Unknown language: {user_language}")
        return None
    
    def get_regional_cuisine_context(self, location: LocationInfo) -> RegionalContext:
        """Возвращает контекст региональной кухни для локации"""
        try:
            cuisine_data = get_regional_cuisine(location.country_code)
            
            return RegionalContext(
                cuisine_types=cuisine_data["cuisine_types"],
                common_products=cuisine_data["common_products"],
                seasonal_products=cuisine_data["seasonal_products"],
                cooking_methods=cuisine_data["cooking_methods"],
                measurement_units=cuisine_data["measurement_units"],
                dietary_preferences=cuisine_data["dietary_preferences"],
                food_culture_notes=cuisine_data["food_culture_notes"],
                region_code=cuisine_data["region_code"]
            )
            
        except Exception as e:
            logger.error(f"❌ Error getting regional context: {e}")
            # Fallback на default кухню
            default_cuisine = get_default_cuisine()
            return RegionalContext(
                cuisine_types=default_cuisine["cuisine_types"],
                common_products=default_cuisine["common_products"],
                seasonal_products=default_cuisine["seasonal_products"],
                cooking_methods=default_cuisine["cooking_methods"],
                measurement_units=default_cuisine["measurement_units"],
                dietary_preferences=default_cuisine["dietary_preferences"],
                food_culture_notes=default_cuisine["food_culture_notes"],
                region_code=default_cuisine["region_code"]
            )
    
    def _get_cached_location(self, user_id: str) -> Optional[LocationCache]:
        """Получение локации из кэша"""
        if user_id in self.location_cache:
            cached = self.location_cache[user_id]
            if not cached.is_expired():
                return cached
            else:
                # Удаляем устаревший кэш
                del self.location_cache[user_id]
                logger.debug(f"🗑️ Expired cache removed for user {user_id}")
        
        return None
    
    async def _cache_location(self, user_id: str, location: LocationInfo, regional_context: RegionalContext):
        """Кэширование локации пользователя"""
        try:
            cache_entry = LocationCache(
                user_id=user_id,
                location_info=location,
                regional_context=regional_context,
                cached_at=datetime.now(),
                expires_at=datetime.now() + self.cache_ttl
            )
            
            self.location_cache[user_id] = cache_entry
            logger.debug(f"💾 Location cached for user {user_id} until {cache_entry.expires_at}")
            
        except Exception as e:
            logger.error(f"❌ Error caching location for user {user_id}: {e}")
    
    def _get_default_location(self, user_language: str) -> LocationInfo:
        """Получение локации по умолчанию"""
        # Используем настройки из конфигурации
        default_country = EnvironmentConfig.DEFAULT_COUNTRY
        default_timezone = EnvironmentConfig.DEFAULT_TIMEZONE
        
        # Определяем название страны
        country_names = {
            "RU": "Russia",
            "US": "United States",
            "DE": "Germany",
            "FR": "France",
            "IT": "Italy",
            "JP": "Japan"
        }
        
        return LocationInfo(
            country_code=default_country,
            country_name=country_names.get(default_country, "Unknown"),
            region="Default Region",
            city=None,
            timezone=default_timezone,
            latitude=None,
            longitude=None,
            confidence=DetectionConfidence.DEFAULT,
            detection_method=DetectionMethod.DEFAULT
        )
    
    async def update_user_location_cache(self, telegram_user_id: str, location: LocationInfo):
        """Обновление кэша локации пользователя"""
        try:
            regional_context = self.get_regional_cuisine_context(location)
            await self._cache_location(telegram_user_id, location, regional_context)
            logger.info(f"✅ Location cache updated for user {telegram_user_id}")
        except Exception as e:
            logger.error(f"❌ Error updating location cache for user {telegram_user_id}: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        total_entries = len(self.location_cache)
        expired_entries = sum(1 for cache in self.location_cache.values() if cache.is_expired())
        active_entries = total_entries - expired_entries
        
        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "cache_hit_rate": "N/A",  # Требует дополнительного трекинга
            "oldest_entry": min(
                (cache.cached_at for cache in self.location_cache.values()),
                default=None
            ),
            "newest_entry": max(
                (cache.cached_at for cache in self.location_cache.values()),
                default=None
            )
        }
    
    async def cleanup_expired_cache(self):
        """Очистка устаревшего кэша"""
        expired_keys = [
            user_id for user_id, cache in self.location_cache.items()
            if cache.is_expired()
        ]
        
        for user_id in expired_keys:
            del self.location_cache[user_id]
        
        if expired_keys:
            logger.info(f"🗑️ Cleaned up {len(expired_keys)} expired cache entries")
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверка здоровья детектора локации"""
        health_status = {
            "detector_healthy": True,
            "providers": {},
            "cache_stats": self.get_cache_stats(),
            "errors": []
        }
        
        # Проверяем провайдеры
        try:
            # Telegram provider
            health_status["providers"]["telegram"] = {
                "configured": self.telegram_provider.is_configured(),
                "healthy": await self.telegram_provider.test_connection() if self.telegram_provider.is_configured() else False
            }
        except Exception as e:
            health_status["providers"]["telegram"] = {"configured": False, "healthy": False, "error": str(e)}
            health_status["errors"].append(f"Telegram provider error: {e}")
        
        try:
            # IP provider
            health_status["providers"]["ip_geolocation"] = {
                "configured": self.ip_provider.is_configured(),
                "services": self.ip_provider.get_configured_services()
            }
        except Exception as e:
            health_status["providers"]["ip_geolocation"] = {"configured": False, "error": str(e)}
            health_status["errors"].append(f"IP geolocation provider error: {e}")
        
        # Общий статус
        if health_status["errors"]:
            health_status["detector_healthy"] = False
        
        return health_status