"""
Internationalization (i18n) module for c0r.ai Telegram Bot
Handles language detection, translations, and language switching
"""
from typing import Dict, Optional, List
from enum import Enum
import re
from loguru import logger


class Language(Enum):
    """Supported languages"""
    ENGLISH = "en"
    RUSSIAN = "ru"


class I18nManager:
    """Manages internationalization for the bot"""
    
    # Countries that default to Russian
    RUSSIAN_COUNTRIES = {
        "RU",  # Russia
        "BY",  # Belarus
        "KZ",  # Kazakhstan
        "KG",  # Kyrgyzstan
        "AM",  # Armenia
        "AZ",  # Azerbaijan
        "GE",  # Georgia
        "UZ",  # Uzbekistan
    }
    
    # Phone number patterns for Russian-speaking countries
    RUSSIAN_PHONE_PATTERNS = [
        r'^\+7',  # +7 (Russia)
        r'^8',    # 8 (Russia)
        r'^\+375',  # +375 (Belarus)
        r'^\+7[0-9]{10}$',  # +7XXXXXXXXXX
        r'^8[0-9]{10}$',    # 8XXXXXXXXXX
    ]
    
    def __init__(self):
        self.translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """Load all translations from modular files"""
        try:
            # Import from new modular structure
            from .en import TRANSLATIONS as EN_TRANSLATIONS
            from .ru import TRANSLATIONS as RU_TRANSLATIONS
            
            return {
                Language.ENGLISH.value: EN_TRANSLATIONS,
                Language.RUSSIAN.value: RU_TRANSLATIONS,
            }
        except ImportError as e:
            logger.error(f"Failed to import modular translation files: {e}")
            # Fallback to original files if modular import fails
            try:
                from .en import TRANSLATIONS as EN_TRANSLATIONS
                from .ru import TRANSLATIONS as RU_TRANSLATIONS
                
                return {
                    Language.ENGLISH.value: EN_TRANSLATIONS,
                    Language.RUSSIAN.value: RU_TRANSLATIONS,
                }
            except ImportError as e2:
                logger.error(f"Failed to import fallback translation files: {e2}")
                return {
                    Language.ENGLISH.value: {},
                    Language.RUSSIAN.value: {},
                }
    
    def detect_language(self, user_country: Optional[str] = None, phone_number: Optional[str] = None) -> str:
        """
        Detect user's preferred language based on country and phone number
        
        Args:
            user_country: User's country code (e.g., 'RU', 'US')
            phone_number: User's phone number
            
        Returns:
            Language code ('en' or 'ru')
        """
        # Check country first
        if user_country and user_country.upper() in self.RUSSIAN_COUNTRIES:
            logger.info(f"Detected Russian language for country: {user_country}")
            return Language.RUSSIAN.value
        
        # Check phone number patterns
        if phone_number:
            for pattern in self.RUSSIAN_PHONE_PATTERNS:
                if re.match(pattern, phone_number):
                    logger.info(f"Detected Russian language for phone: {phone_number}")
                    return Language.RUSSIAN.value
        
        # Default to English
        logger.info(f"Defaulting to English language for country: {user_country}, phone: {phone_number}")
        return Language.ENGLISH.value
    
    def get_text(self, key: str, language: str = Language.ENGLISH.value, **kwargs) -> str:
        """
        Get translated text for a given key and language
        
        Args:
            key: Translation key
            language: Language code ('en' or 'ru')
            **kwargs: Format parameters for the text
            
        Returns:
            Translated and formatted text
        """
        if language not in self.translations:
            logger.warning(f"Language {language} not found, falling back to English")
            language = Language.ENGLISH.value
        
        if key not in self.translations[language]:
            logger.warning(f"Translation key '{key}' not found for language {language}")
            # Fallback to English
            if key in self.translations[Language.ENGLISH.value]:
                text = self.translations[Language.ENGLISH.value][key]
            else:
                return f"[Missing translation: {key}]"
        else:
            text = self.translations[language][key]
        
        # Format the text with provided parameters
        try:
            return text.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing format parameter {e} for key '{key}' in language {language}")
            return text
    
    def get_language_name(self, language_code: str) -> str:
        """Get human-readable language name"""
        language_names = {
            Language.ENGLISH.value: "English",
            Language.RUSSIAN.value: "Русский"
        }
        return language_names.get(language_code, "Unknown")


# Global instance
i18n = I18nManager() 