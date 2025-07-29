"""
IP Geolocation Provider for c0r.AI ML Service
Location detection through IP address geolocation services
"""

import asyncio
from typing import Optional, Dict, Any, List
import httpx
from loguru import logger

from ..models import LocationInfo, DetectionMethod, DetectionConfidence
from ....core.models.config.environment_config import EnvironmentConfig


class IPGeolocationProvider:
    """Провайдер геолокации по IP адресу"""
    
    def __init__(self):
        self.maxmind_key = EnvironmentConfig.MAXMIND_LICENSE_KEY
        self.ipstack_key = EnvironmentConfig.IPSTACK_API_KEY
        self.timeout = 10
        
        # Приоритет сервисов (от лучшего к худшему)
        self.services = [
            self._get_location_maxmind,
            self._get_location_ipstack,
            self._get_location_ipapi,  # Бесплатный fallback
        ]
    
    async def get_location(self, ip_address: str) -> Optional[LocationInfo]:
        """
        Определение локации по IP адресу
        
        Args:
            ip_address: IP адрес для определения локации
            
        Returns:
            LocationInfo или None если определить не удалось
        """
        if not ip_address or ip_address in ['127.0.0.1', 'localhost', '::1']:
            logger.debug("❌ Invalid or local IP address provided")
            return None
        
        logger.debug(f"🌐 Determining location for IP: {ip_address}")
        
        # Пробуем сервисы по приоритету
        for service_func in self.services:
            try:
                location = await service_func(ip_address)
                if location:
                    logger.info(f"✅ IP location found via {service_func.__name__}: {location.country_code}")
                    return location
            except Exception as e:
                logger.debug(f"❌ {service_func.__name__} failed: {e}")
                continue
        
        logger.warning(f"❌ Failed to determine location for IP: {ip_address}")
        return None
    
    async def _get_location_maxmind(self, ip_address: str) -> Optional[LocationInfo]:
        """Получение локации через MaxMind GeoIP2"""
        if not self.maxmind_key:
            logger.debug("🔑 MaxMind license key not configured")
            return None
        
        try:
            url = f"https://geoip.maxmind.com/geoip/v2.1/city/{ip_address}"
            headers = {
                "Authorization": f"Basic {self.maxmind_key}",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_maxmind_response(data, ip_address)
                else:
                    logger.debug(f"❌ MaxMind API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.debug(f"❌ MaxMind request error: {e}")
            return None
    
    async def _get_location_ipstack(self, ip_address: str) -> Optional[LocationInfo]:
        """Получение локации через IPStack"""
        if not self.ipstack_key:
            logger.debug("🔑 IPStack API key not configured")
            return None
        
        try:
            url = f"http://api.ipstack.com/{ip_address}"
            params = {
                "access_key": self.ipstack_key,
                "format": 1
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if not data.get("error"):
                        return self._parse_ipstack_response(data, ip_address)
                    else:
                        logger.debug(f"❌ IPStack API error: {data['error']}")
                        return None
                else:
                    logger.debug(f"❌ IPStack HTTP error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.debug(f"❌ IPStack request error: {e}")
            return None
    
    async def _get_location_ipapi(self, ip_address: str) -> Optional[LocationInfo]:
        """Получение локации через IP-API (бесплатный сервис)"""
        try:
            url = f"http://ip-api.com/json/{ip_address}"
            params = {
                "fields": "status,message,country,countryCode,region,regionName,city,lat,lon,timezone"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "success":
                        return self._parse_ipapi_response(data, ip_address)
                    else:
                        logger.debug(f"❌ IP-API error: {data.get('message', 'Unknown error')}")
                        return None
                else:
                    logger.debug(f"❌ IP-API HTTP error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.debug(f"❌ IP-API request error: {e}")
            return None
    
    def _parse_maxmind_response(self, data: Dict[str, Any], ip_address: str) -> LocationInfo:
        """Парсинг ответа MaxMind"""
        try:
            country = data.get("country", {})
            subdivisions = data.get("subdivisions", [])
            city = data.get("city", {})
            location = data.get("location", {})
            
            return LocationInfo(
                country_code=country.get("iso_code", "UNKNOWN"),
                country_name=country.get("names", {}).get("en", "Unknown"),
                region=subdivisions[0].get("names", {}).get("en", "Unknown") if subdivisions else "Unknown",
                city=city.get("names", {}).get("en"),
                timezone=location.get("time_zone"),
                latitude=location.get("latitude"),
                longitude=location.get("longitude"),
                confidence=DetectionConfidence.MEDIUM,
                detection_method=DetectionMethod.IP_GEOLOCATION
            )
        except Exception as e:
            logger.error(f"❌ Error parsing MaxMind response: {e}")
            raise
    
    def _parse_ipstack_response(self, data: Dict[str, Any], ip_address: str) -> LocationInfo:
        """Парсинг ответа IPStack"""
        try:
            return LocationInfo(
                country_code=data.get("country_code", "UNKNOWN"),
                country_name=data.get("country_name", "Unknown"),
                region=data.get("region_name", "Unknown"),
                city=data.get("city"),
                timezone=data.get("time_zone", {}).get("id") if data.get("time_zone") else None,
                latitude=data.get("latitude"),
                longitude=data.get("longitude"),
                confidence=DetectionConfidence.MEDIUM,
                detection_method=DetectionMethod.IP_GEOLOCATION
            )
        except Exception as e:
            logger.error(f"❌ Error parsing IPStack response: {e}")
            raise
    
    def _parse_ipapi_response(self, data: Dict[str, Any], ip_address: str) -> LocationInfo:
        """Парсинг ответа IP-API"""
        try:
            return LocationInfo(
                country_code=data.get("countryCode", "UNKNOWN"),
                country_name=data.get("country", "Unknown"),
                region=data.get("regionName", "Unknown"),
                city=data.get("city"),
                timezone=data.get("timezone"),
                latitude=data.get("lat"),
                longitude=data.get("lon"),
                confidence=DetectionConfidence.MEDIUM,
                detection_method=DetectionMethod.IP_GEOLOCATION
            )
        except Exception as e:
            logger.error(f"❌ Error parsing IP-API response: {e}")
            raise
    
    async def get_client_ip_from_request(self, request_headers: Dict[str, str]) -> Optional[str]:
        """
        Извлечение IP адреса клиента из заголовков запроса
        
        Args:
            request_headers: Заголовки HTTP запроса
            
        Returns:
            IP адрес клиента или None
        """
        # Проверяем различные заголовки в порядке приоритета
        ip_headers = [
            "CF-Connecting-IP",      # Cloudflare
            "X-Forwarded-For",       # Стандартный прокси заголовок
            "X-Real-IP",             # Nginx
            "X-Client-IP",           # Apache
            "X-Forwarded",           # Общий
            "Forwarded-For",         # RFC 7239
            "Forwarded",             # RFC 7239
        ]
        
        for header in ip_headers:
            ip = request_headers.get(header)
            if ip:
                # X-Forwarded-For может содержать несколько IP через запятую
                if "," in ip:
                    ip = ip.split(",")[0].strip()
                
                # Проверяем, что это валидный IP
                if self._is_valid_ip(ip):
                    logger.debug(f"🌐 Client IP found in {header}: {ip}")
                    return ip
        
        logger.debug("❌ No valid client IP found in headers")
        return None
    
    def _is_valid_ip(self, ip: str) -> bool:
        """Проверка валидности IP адреса"""
        try:
            import ipaddress
            ipaddress.ip_address(ip)
            
            # Исключаем локальные и приватные адреса
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                return False
            
            return True
        except ValueError:
            return False
    
    async def test_services(self) -> Dict[str, bool]:
        """Тестирование доступности всех сервисов"""
        test_ip = "8.8.8.8"  # Google DNS для тестирования
        results = {}
        
        for service_func in self.services:
            try:
                location = await service_func(test_ip)
                results[service_func.__name__] = location is not None
                if location:
                    logger.info(f"✅ {service_func.__name__} test successful")
                else:
                    logger.warning(f"❌ {service_func.__name__} test failed")
            except Exception as e:
                results[service_func.__name__] = False
                logger.error(f"❌ {service_func.__name__} test error: {e}")
        
        return results
    
    def get_configured_services(self) -> List[str]:
        """Получение списка настроенных сервисов"""
        configured = []
        
        if self.maxmind_key:
            configured.append("MaxMind GeoIP2")
        if self.ipstack_key:
            configured.append("IPStack")
        
        configured.append("IP-API (free)")  # Всегда доступен
        
        return configured
    
    def is_configured(self) -> bool:
        """Проверка конфигурации провайдера"""
        # Провайдер считается настроенным, если есть хотя бы один бесплатный сервис
        return True