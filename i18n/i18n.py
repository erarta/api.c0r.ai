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
    
    # Language detection based on Telegram language_code
    CIS_LANGUAGES = {
        'ru',  # Russian
        'kk',  # Kazakh
        'be',  # Belarusian
        'uz',  # Uzbek
        'ky',  # Kyrgyz
        'tg',  # Tajik
        'tk',  # Turkmen
        'hy',  # Armenian
        'az',  # Azerbaijani
        'mo',  # Moldovan
        'uk',  # Ukrainian
    }
    
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
    
    def detect_language(self, language_code: Optional[str] = None) -> str:
        """
        Detect user's preferred language based on Telegram language_code
        
        Args:
            language_code: Telegram language_code (e.g., 'ru', 'en', 'de')
            
        Returns:
            Language code ('en' or 'ru')
        """
        if not language_code:
            return Language.ENGLISH.value
        
        # Normalize language code
        lang = language_code.lower().strip()
        
        # Check if it's a CIS language
        if lang in self.CIS_LANGUAGES:
            logger.info(f"Detected Russian language for language_code: {language_code}")
            return Language.RUSSIAN.value
        
        # Default to English
        logger.info(f"Defaulting to English language for language_code: {language_code}")
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
    
    def get_random_header(self, header_key: str, language: str = Language.ENGLISH.value) -> str:
        """Get a random header from an array of creative headers"""
        import random
        
        headers_array = self.translations.get(language, {}).get(header_key, [])
        
        if isinstance(headers_array, list) and headers_array:
            return random.choice(headers_array)
        
        # Fallback to regular key without '_headers' suffix
        fallback_key = header_key.replace('_headers', '')
        return self.get_text(fallback_key, language)

    def get_random_fact(self, language: str = Language.ENGLISH.value) -> str:
        """
        Get a random interesting food fact
        
        Args:
            language: Language code
            
        Returns:
            Random food fact string
        """
        try:
            from i18n.food_facts import FOOD_FACTS, FACT_EXTENSIONS
            
            facts = FOOD_FACTS.get(language, FOOD_FACTS.get("en", []))
            if facts:
                import random
                base = random.choice(facts)
                # Optionally extend the fact with a longer explanatory tail
                extensions = FACT_EXTENSIONS.get(language, FACT_EXTENSIONS.get("en", []))
                if extensions:
                    tail = random.choice(extensions)
                    return f"{base}. {tail}"
                return base
        except ImportError:
            pass
        return "🍎 Food is amazing!"

    def get_random_waiting_phrase(self, language: str = Language.ENGLISH.value) -> str:
        """
        Get a random waiting phrase for analysis
        
        Args:
            language: Language code
            
        Returns:
            Random waiting phrase string
        """
        try:
            from i18n.food_facts import WAITING_PHRASES
            
            phrases = WAITING_PHRASES.get(language, WAITING_PHRASES.get("en", []))
            if phrases:
                import random
                return random.choice(phrases)
        except ImportError:
            pass
        return "Analyzing your food... ⏳"

    def get_random_waiting_phrase(self, language: str = Language.ENGLISH.value) -> str:
        """
        Get a random waiting phrase for analysis
        
        Args:
            language: Language code
            
        Returns:
            Random waiting phrase string
        """
        try:
            from i18n.food_facts import WAITING_PHRASES
            
            phrases = WAITING_PHRASES.get(language, WAITING_PHRASES.get("en", []))
            if phrases:
                import random
                return random.choice(phrases)
        except ImportError:
            pass
        return "Analyzing your food... ⏳"


# Global instance
i18n = I18nManager() 