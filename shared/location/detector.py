"""
User Location Detector for c0r.AI
Main location detection system with multiple providers and fallback strategies
"""

import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

from .models import (
    LocationInfo, RegionalContext, LocationResult,
    DetectionSource, DetectionConfidence
)
from .regional_data.cuisines import get_regional_cuisine, get_default_cuisine


class LocationDetector:
    """Основной класс для определения локации пользователя"""
    
    def __init__(self, cache_ttl_hours: int = 24):
        # Кэш локаций пользователей
        self.location_cache: Dict[str, Dict[str, Any]] = {}
        
        # Настройки кэширования (24 часа по умолчанию)
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
        # Fallback цепочка
        self.detection_chain = [
            self._detect_via_telegram,
            self._detect_via_ip,
            self._detect_via_timezone,
            self._detect_via_language_fallback
        ]
        
        logger.info("🌍 LocationDetector initialized")
    
    async def detect_location(self, 
                            user_id: str, 
                            language: str = "en",
                            ip_address: Optional[str] = None,
                            timezone: Optional[str] = None,
                            telegram_data: Optional[Dict[str, Any]] = None) -> LocationResult:
        """
        Определяет локацию пользователя используя несколько методов
        
        Args:
            user_id: ID пользователя
            language: Язык пользователя
            ip_address: IP адрес (опционально)
            timezone: Временная зона (опционально)
            telegram_data: Данные из Telegram (опционально)
            
        Returns:
            LocationResult с информацией о локации
        """
        logger.info(f"🔍 Detecting location for user {user_id}")
        
        try:
            # Проверяем кэш
            cached_location = self._get_cached_location(user_id)
            if cached_location:
                logger.info(f"✅ Using cached location for user {user_id}: {cached_location['location'].country_code}")
                return LocationResult(
                    location=cached_location['location'],
                    regional_context=cached_location['regional_context'],
                    success=True,
                    cache_hit=True
                )
            
            # Подготавливаем контекст для детекции
            detection_context = {
                "user_id": user_id,
                "language": language,
                "ip_address": ip_address,
                "timezone": timezone,
                "telegram_data": telegram_data or {}
            }
            
            # Пробуем методы детекции по порядку
            for detection_method in self.detection_chain:
                try:
                    location = await detection_method(detection_context)
                    if location:
                        # Получаем региональный контекст
                        regional_context = self.get_regional_context(location)
                        
                        # Кэшируем результат
                        await self._cache_location(user_id, location, regional_context)
                        
                        logger.info(f"✅ Location detected for user {user_id}: {location.country_code} via {location.source}")
                        
                        return LocationResult(
                            location=location,
                            regional_context=regional_context,
                            success=True,
                            fallback_used=location.source != DetectionSource.TELEGRAM
                        )
                        
                except Exception as e:
                    logger.warning(f"⚠️ Detection method {detection_method.__name__} failed: {e}")
                    continue
            
            # Все методы не сработали - используем fallback по умолчанию
            logger.warning(f"❌ All detection methods failed for user {user_id}, using default")
            
            default_location = self._get_default_location(language)
            default_context = self.get_regional_context(default_location)
            
            return LocationResult(
                location=default_location,
                regional_context=default_context,
                success=True,
                fallback_used=True
            )
            
        except Exception as e:
            logger.error(f"❌ Location detection error for user {user_id}: {e}")
            
            # Критическая ошибка - возвращаем default
            default_location = self._get_default_location(language)
            default_context = self.get_regional_context(default_location)
            
            return LocationResult(
                location=default_location,
                regional_context=default_context,
                success=False,
                error_message=str(e),
                fallback_used=True
            )
    
    async def _detect_via_telegram(self, context: Dict[str, Any]) -> Optional[LocationInfo]:
        """Определение через Telegram API"""
        telegram_data = context.get("telegram_data", {})
        
        # Проверяем наличие данных локации в Telegram
        if not telegram_data or "location" not in telegram_data:
            logger.debug("🤖 No Telegram location data provided")
            return None
        
        location_data = telegram_data["location"]
        
        # Извлекаем координаты
        latitude = location_data.get("latitude")
        longitude = location_data.get("longitude")
        
        if not latitude or not longitude:
            logger.debug("🤖 Invalid Telegram location coordinates")
            return None
        
        # Здесь можно добавить обратное геокодирование для получения адреса
        # Пока используем базовую информацию
        
        return LocationInfo(
            country_code="US",  # Placeholder - нужно реализовать обратное геокодирование
            country_name="United States",
            region="Unknown",
            city=None,
            timezone=None,
            latitude=latitude,
            longitude=longitude,
            confidence=DetectionConfidence.HIGH,
            source=DetectionSource.TELEGRAM,
            language=context.get("language")
        )
    
    async def _detect_via_ip(self, context: Dict[str, Any]) -> Optional[LocationInfo]:
        """Определение через IP геолокацию"""
        ip_address = context.get("ip_address")
        if not ip_address:
            logger.debug("🌐 No IP address provided for geolocation")
            return None
        
        # Здесь должна быть интеграция с IP геолокационным сервисом
        # Пока возвращаем заглушку
        logger.debug(f"🌐 IP geolocation for {ip_address} not implemented")
        return None
    
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
            "Asia/Dubai": ("AE", "United Arab Emirates", "Dubai"),
            "Asia/Riyadh": ("SA", "Saudi Arabia", "Riyadh"),
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
                source=DetectionSource.TIMEZONE,
                language=context.get("language")
            )
        
        logger.debug(f"🕐 Unknown timezone: {timezone}")
        return None
    
    async def _detect_via_language_fallback(self, context: Dict[str, Any]) -> Optional[LocationInfo]:
        """Fallback определение по языку пользователя"""
        language = context["language"]
        
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
            "ar": ("SA", "Saudi Arabia", "Middle East"),
        }
        
        if language in language_mapping:
            country_code, country_name, region = language_mapping[language]
            
            logger.debug(f"🗣️ Location fallback via language {language}: {country_code}")
            
            return LocationInfo(
                country_code=country_code,
                country_name=country_name,
                region=region,
                city=None,
                timezone=None,
                latitude=None,
                longitude=None,
                confidence=DetectionConfidence.VERY_LOW,
                source=DetectionSource.LANGUAGE,
                language=language
            )
        
        logger.debug(f"🗣️ Unknown language: {language}")
        return None
    
    def get_regional_context(self, location: LocationInfo) -> RegionalContext:
        """Возвращает контекст региональной кухни для локации"""
        try:
            cuisine_data = get_regional_cuisine(location.country_code)
            
            return RegionalContext(
                region_code=cuisine_data["region_code"],
                cuisine_types=cuisine_data["cuisine_types"],
                common_products=cuisine_data["common_products"],
                seasonal_products=cuisine_data["seasonal_products"],
                cooking_methods=cuisine_data["cooking_methods"],
                measurement_units=cuisine_data["measurement_units"],
                dietary_preferences=cuisine_data["dietary_preferences"],
                food_culture_notes=cuisine_data["food_culture_notes"]
            )
            
        except Exception as e:
            logger.error(f"❌ Error getting regional context: {e}")
            # Fallback на default кухню
            default_cuisine = get_default_cuisine()
            return RegionalContext(
                region_code=default_cuisine["region_code"],
                cuisine_types=default_cuisine["cuisine_types"],
                common_products=default_cuisine["common_products"],
                seasonal_products=default_cuisine["seasonal_products"],
                cooking_methods=default_cuisine["cooking_methods"],
                measurement_units=default_cuisine["measurement_units"],
                dietary_preferences=default_cuisine["dietary_preferences"],
                food_culture_notes=default_cuisine["food_culture_notes"]
            )
    
    def _get_cached_location(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Получение локации из кэша"""
        if user_id in self.location_cache:
            cached = self.location_cache[user_id]
            cached_at = datetime.fromisoformat(cached["cached_at"])
            
            if datetime.now() - cached_at < self.cache_ttl:
                return cached
            else:
                # Удаляем устаревший кэш
                del self.location_cache[user_id]
                logger.debug(f"🗑️ Expired cache removed for user {user_id}")
        
        return None
    
    async def _cache_location(self, user_id: str, location: LocationInfo, regional_context: RegionalContext):
        """Кэширование локации пользователя"""
        try:
            cache_entry = {
                "user_id": user_id,
                "location": location,
                "regional_context": regional_context,
                "cached_at": datetime.now().isoformat()
            }
            
            self.location_cache[user_id] = cache_entry
            logger.debug(f"💾 Location cached for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error caching location for user {user_id}: {e}")
    
    def _get_default_location(self, language: str) -> LocationInfo:
        """Получение локации по умолчанию"""
        # Определяем страну по умолчанию на основе языка
        default_countries = {
            "ru": ("RU", "Russia"),
            "en": ("US", "United States"),
            "de": ("DE", "Germany"),
            "fr": ("FR", "France"),
            "it": ("IT", "Italy"),
            "ja": ("JP", "Japan"),
            "ar": ("SA", "Saudi Arabia")
        }
        
        country_code, country_name = default_countries.get(language, ("US", "United States"))
        
        return LocationInfo(
            country_code=country_code,
            country_name=country_name,
            region="Default Region",
            city=None,
            timezone=None,
            latitude=None,
            longitude=None,
            confidence=DetectionConfidence.DEFAULT,
            source=DetectionSource.DEFAULT,
            language=language
        )
    
    async def update_location_cache(self, user_id: str, location: LocationInfo):
        """Обновление кэша локации пользователя"""
        try:
            regional_context = self.get_regional_context(location)
            await self._cache_location(user_id, location, regional_context)
            logger.info(f"✅ Location cache updated for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error updating location cache for user {user_id}: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        total_entries = len(self.location_cache)
        
        # Подсчитываем устаревшие записи
        expired_entries = 0
        oldest_entry = None
        newest_entry = None
        
        for cache in self.location_cache.values():
            cached_at = datetime.fromisoformat(cache["cached_at"])
            
            if datetime.now() - cached_at >= self.cache_ttl:
                expired_entries += 1
            
            if oldest_entry is None or cached_at < oldest_entry:
                oldest_entry = cached_at
            
            if newest_entry is None or cached_at > newest_entry:
                newest_entry = cached_at
        
        active_entries = total_entries - expired_entries
        
        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "expired_entries": expired_entries,
            "cache_ttl_hours": self.cache_ttl.total_seconds() / 3600,
            "oldest_entry": oldest_entry.isoformat() if oldest_entry else None,
            "newest_entry": newest_entry.isoformat() if newest_entry else None
        }
    
    async def cleanup_expired_cache(self):
        """Очистка устаревшего кэша"""
        expired_keys = []
        
        for user_id, cache in self.location_cache.items():
            cached_at = datetime.fromisoformat(cache["cached_at"])
            if datetime.now() - cached_at >= self.cache_ttl:
                expired_keys.append(user_id)
        
        for user_id in expired_keys:
            del self.location_cache[user_id]
        
        if expired_keys:
            logger.info(f"🗑️ Cleaned up {len(expired_keys)} expired cache entries")