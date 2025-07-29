"""
Location Models for c0r.AI
Data models for location detection and regional context
"""

from dataclasses import dataclass
from typing import Optional, Dict, List, Any
from datetime import datetime


@dataclass
class LocationInfo:
    """Информация о локации пользователя"""
    country_code: str           # ISO код страны (RU, US, DE, AE, SA)
    country_name: str           # Название страны
    region: str                 # Регион/область
    city: Optional[str]         # Город (если доступен)
    timezone: Optional[str]     # Временная зона
    latitude: Optional[float]   # Широта
    longitude: Optional[float]  # Долгота
    confidence: float           # Уверенность в определении (0-1)
    source: str                 # Источник определения
    language: Optional[str]     # Язык пользователя
    detected_at: datetime = None
    
    def __post_init__(self):
        if self.detected_at is None:
            self.detected_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "country_code": self.country_code,
            "country_name": self.country_name,
            "region": self.region,
            "city": self.city,
            "timezone": self.timezone,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "confidence": self.confidence,
            "source": self.source,
            "language": self.language,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LocationInfo':
        """Создание из словаря"""
        detected_at = None
        if data.get('detected_at'):
            detected_at = datetime.fromisoformat(data['detected_at'])
        
        return cls(
            country_code=data['country_code'],
            country_name=data['country_name'],
            region=data['region'],
            city=data.get('city'),
            timezone=data.get('timezone'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            confidence=data['confidence'],
            source=data['source'],
            language=data.get('language'),
            detected_at=detected_at
        )


@dataclass
class RegionalContext:
    """Контекст региональной кухни"""
    region_code: str                           # Код региона
    cuisine_types: List[str]                   # Типы кухни
    common_products: List[str]                 # Распространенные продукты
    seasonal_products: Dict[str, List[str]]    # Сезонные продукты
    cooking_methods: List[str]                 # Популярные методы готовки
    measurement_units: str                     # Единицы измерения (metric/imperial)
    dietary_preferences: List[str]             # Популярные диеты в регионе
    food_culture_notes: str                    # Особенности пищевой культуры
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "region_code": self.region_code,
            "cuisine_types": self.cuisine_types,
            "common_products": self.common_products,
            "seasonal_products": self.seasonal_products,
            "cooking_methods": self.cooking_methods,
            "measurement_units": self.measurement_units,
            "dietary_preferences": self.dietary_preferences,
            "food_culture_notes": self.food_culture_notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RegionalContext':
        """Создание из словаря"""
        return cls(
            region_code=data['region_code'],
            cuisine_types=data['cuisine_types'],
            common_products=data['common_products'],
            seasonal_products=data['seasonal_products'],
            cooking_methods=data['cooking_methods'],
            measurement_units=data['measurement_units'],
            dietary_preferences=data['dietary_preferences'],
            food_culture_notes=data['food_culture_notes']
        )


@dataclass
class LocationResult:
    """Результат определения локации"""
    location: Optional[LocationInfo]
    regional_context: Optional[RegionalContext]
    success: bool = True
    error_message: Optional[str] = None
    fallback_used: bool = False
    cache_hit: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование в словарь"""
        return {
            "location": self.location.to_dict() if self.location else None,
            "regional_context": self.regional_context.to_dict() if self.regional_context else None,
            "success": self.success,
            "error_message": self.error_message,
            "fallback_used": self.fallback_used,
            "cache_hit": self.cache_hit
        }


class DetectionSource:
    """Источники определения локации"""
    TELEGRAM = "telegram"
    IP = "ip"
    TIMEZONE = "timezone"
    LANGUAGE = "language"
    CACHED = "cached"
    DEFAULT = "default"


class DetectionConfidence:
    """Уровни уверенности в определении"""
    HIGH = 0.9      # Telegram API с точными данными
    MEDIUM = 0.7    # IP геолокация
    LOW = 0.4       # Timezone mapping
    VERY_LOW = 0.2  # Language fallback
    DEFAULT = 0.1   # Default fallback