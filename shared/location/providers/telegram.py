"""
Telegram Location Provider for c0r.AI ML Service
Location detection through Telegram Bot API
"""

import asyncio
from typing import Optional
import httpx
from loguru import logger

from ..models import LocationInfo, DetectionMethod, DetectionConfidence
from ....core.models.config.environment_config import EnvironmentConfig


class TelegramLocationProvider:
    """Провайдер геолокации через Telegram API"""
    
    def __init__(self):
        self.bot_token = EnvironmentConfig.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
        self.timeout = 10
    
    async def get_location(self, telegram_user_id: str) -> Optional[LocationInfo]:
        """
        Получение локации пользователя из Telegram
        
        Args:
            telegram_user_id: ID пользователя в Telegram
            
        Returns:
            LocationInfo или None если локация недоступна
        """
        if not self.bot_token:
            logger.warning("🤖 Telegram bot token not configured")
            return None
        
        try:
            logger.debug(f"🔍 Checking Telegram location for user {telegram_user_id}")
            
            # Получаем информацию о пользователе
            user_info = await self._get_user_info(telegram_user_id)
            if not user_info:
                logger.debug(f"❌ No user info found for {telegram_user_id}")
                return None
            
            # Проверяем последние сообщения с геолокацией
            location_data = await self._get_recent_location_messages(telegram_user_id)
            if location_data:
                logger.info(f"✅ Found Telegram location for user {telegram_user_id}")
                return self._create_location_info(location_data, user_info)
            
            # Проверяем настройки локации в профиле
            profile_location = await self._get_profile_location(telegram_user_id)
            if profile_location:
                logger.info(f"✅ Found Telegram profile location for user {telegram_user_id}")
                return self._create_location_info(profile_location, user_info)
            
            logger.debug(f"❌ No location data found in Telegram for user {telegram_user_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Telegram location error for user {telegram_user_id}: {e}")
            return None
    
    async def _get_user_info(self, telegram_user_id: str) -> Optional[dict]:
        """Получение информации о пользователе"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/getChat",
                    params={"chat_id": telegram_user_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        return data.get("result")
                
                logger.debug(f"❌ Failed to get user info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.debug(f"❌ Error getting user info: {e}")
            return None
    
    async def _get_recent_location_messages(self, telegram_user_id: str) -> Optional[dict]:
        """
        Получение последних сообщений с геолокацией
        
        Note: В реальной реализации нужно будет использовать webhook или 
        сохраненные данные о локации, так как Bot API не позволяет 
        получать историю сообщений напрямую
        """
        try:
            # Здесь должна быть логика получения сохраненных данных о локации
            # из базы данных или кэша, полученных через webhook
            
            # Пока возвращаем None, так как это требует интеграции с базой данных
            logger.debug(f"🔍 Checking saved location data for user {telegram_user_id}")
            
            # TODO: Реализовать получение сохраненных данных о локации
            # saved_location = await self._get_saved_location_from_db(telegram_user_id)
            # return saved_location
            
            return None
            
        except Exception as e:
            logger.debug(f"❌ Error getting recent location messages: {e}")
            return None
    
    async def _get_profile_location(self, telegram_user_id: str) -> Optional[dict]:
        """
        Получение локации из профиля пользователя
        
        Note: Telegram Bot API не предоставляет доступ к локации профиля
        """
        # Telegram Bot API не позволяет получить локацию из профиля пользователя
        # Эта функция оставлена для будущих возможностей API
        return None
    
    def _create_location_info(self, location_data: dict, user_info: dict) -> LocationInfo:
        """Создание LocationInfo из данных Telegram"""
        
        # Извлекаем координаты
        latitude = location_data.get("latitude")
        longitude = location_data.get("longitude")
        
        # Определяем страну и регион по координатам (упрощенная логика)
        country_code, country_name, region = self._coordinates_to_location(latitude, longitude)
        
        # Получаем город из данных пользователя если доступен
        city = None
        if user_info and "location" in user_info:
            city = user_info["location"]
        
        return LocationInfo(
            country_code=country_code,
            country_name=country_name,
            region=region,
            city=city,
            timezone=None,  # Telegram не предоставляет timezone
            latitude=latitude,
            longitude=longitude,
            confidence=DetectionConfidence.HIGH,
            detection_method=DetectionMethod.TELEGRAM_API
        )
    
    def _coordinates_to_location(self, latitude: float, longitude: float) -> tuple:
        """
        Упрощенное определение страны по координатам
        
        В реальной реализации следует использовать reverse geocoding API
        """
        # Упрощенная логика для основных регионов
        if 41 <= latitude <= 82 and 19 <= longitude <= 180:
            if 55 <= latitude <= 70 and 30 <= longitude <= 180:
                return "RU", "Russia", "Central Russia"
            elif 45 <= latitude <= 55 and 2 <= longitude <= 40:
                return "DE", "Germany", "Central Europe"
        elif 24 <= latitude <= 49 and -125 <= longitude <= -66:
            return "US", "United States", "North America"
        elif 35 <= latitude <= 71 and -10 <= longitude <= 40:
            return "FR", "France", "Western Europe"
        elif 35 <= latitude <= 47 and 6 <= longitude <= 19:
            return "IT", "Italy", "Southern Europe"
        elif 30 <= latitude <= 46 and 129 <= longitude <= 146:
            return "JP", "Japan", "East Asia"
        
        # По умолчанию
        return "UNKNOWN", "Unknown", "Unknown Region"
    
    async def test_connection(self) -> bool:
        """Тестирование соединения с Telegram API"""
        if not self.bot_token:
            return False
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/getMe")
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok"):
                        logger.info(f"✅ Telegram API connection successful: {data['result']['username']}")
                        return True
                
                logger.warning(f"❌ Telegram API connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Telegram API connection error: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Проверка конфигурации провайдера"""
        return bool(self.bot_token)
    
    async def save_location_from_webhook(self, telegram_user_id: str, location_data: dict):
        """
        Сохранение данных о локации, полученных через webhook
        
        Args:
            telegram_user_id: ID пользователя
            location_data: Данные о локации из сообщения
        """
        try:
            # TODO: Реализовать сохранение в базу данных или кэш
            logger.info(f"📍 Saving location data for user {telegram_user_id}")
            
            # Пример структуры данных для сохранения:
            location_record = {
                "user_id": telegram_user_id,
                "latitude": location_data.get("latitude"),
                "longitude": location_data.get("longitude"),
                "timestamp": location_data.get("date"),
                "live_period": location_data.get("live_period"),
                "heading": location_data.get("heading"),
                "proximity_alert_radius": location_data.get("proximity_alert_radius")
            }
            
            # await self._save_to_database(location_record)
            logger.debug(f"📍 Location data prepared for saving: {location_record}")
            
        except Exception as e:
            logger.error(f"❌ Error saving location data: {e}")