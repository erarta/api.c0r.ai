#!/usr/bin/env python3
"""
Simple test for i18n functionality without external dependencies
"""
import sys
import os
import re
from enum import Enum

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api.c0r.ai', 'app'))

# Mock logger to avoid dependency
class MockLogger:
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

# Mock the loguru logger
sys.modules['loguru'] = type('MockLoguru', (), {'logger': MockLogger()})

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
    
    def _load_translations(self):
        """Load all translations"""
        return {
            Language.ENGLISH.value: {
                "welcome_title": "🎉 **Welcome to c0r.ai Food Analyzer!**",
                "welcome_greeting": "👋 Hello {name}!",
                "welcome_credits": "💳 You have **{credits} credits** remaining",
                "language_english": "🇺🇸 English",
                "language_russian": "🇷🇺 Русский",
            },
            
            Language.RUSSIAN.value: {
                "welcome_title": "🎉 **Добро пожаловать в c0r.ai Анализатор еды!**",
                "welcome_greeting": "👋 Привет, {name}!",
                "welcome_credits": "💳 У вас осталось **{credits} кредитов**",
                "language_english": "🇺🇸 English",
                "language_russian": "🇷🇺 Русский",
            }
        }
    
    def detect_language(self, user_country=None, phone_number=None):
        """Detect user's preferred language"""
        # Check country first
        if user_country and user_country.upper() in self.RUSSIAN_COUNTRIES:
            print(f"Detected Russian language for country: {user_country}")
            return Language.RUSSIAN.value
        
        # Check phone number patterns
        if phone_number:
            for pattern in self.RUSSIAN_PHONE_PATTERNS:
                if re.match(pattern, phone_number):
                    print(f"Detected Russian language for phone: {phone_number}")
                    return Language.RUSSIAN.value
        
        # Default to English
        print(f"Defaulting to English language for country: {user_country}, phone: {phone_number}")
        return Language.ENGLISH.value
    
    def get_text(self, key, language=Language.ENGLISH.value, **kwargs):
        """Get translated text"""
        if language not in self.translations:
            print(f"Language {language} not found, falling back to English")
            language = Language.ENGLISH.value
        
        if key not in self.translations[language]:
            print(f"Translation key '{key}' not found for language {language}")
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
            print(f"Missing format parameter {e} for key '{key}' in language {language}")
            return text
    
    def get_language_name(self, language_code):
        """Get human-readable language name"""
        language_names = {
            Language.ENGLISH.value: "English",
            Language.RUSSIAN.value: "Русский"
        }
        return language_names.get(language_code, "Unknown")

def test_language_detection():
    """Test language detection functionality"""
    print("🧪 Testing Language Detection...")
    
    i18n = I18nManager()
    
    # Test Russian countries
    russian_countries = ["RU", "BY", "KZ", "KG", "AM", "AZ", "GE", "UZ"]
    for country in russian_countries:
        detected = i18n.detect_language(country)
        print(f"  Country {country}: {detected} {'✅' if detected == 'ru' else '❌'}")
    
    # Test phone numbers
    russian_phones = ["+79001234567", "89001234567", "+375291234567"]
    for phone in russian_phones:
        detected = i18n.detect_language(phone_number=phone)
        print(f"  Phone {phone}: {detected} {'✅' if detected == 'ru' else '❌'}")
    
    # Test English defaults
    english_cases = [
        ("US", None),
        ("GB", None),
        (None, "+1234567890"),
        (None, None)
    ]
    for country, phone in english_cases:
        detected = i18n.detect_language(country, phone)
        print(f"  Country {country}, Phone {phone}: {detected} {'✅' if detected == 'en' else '❌'}")

def test_translations():
    """Test translation functionality"""
    print("\n🌐 Testing Translations...")
    
    i18n = I18nManager()
    
    # Test English translations
    print("  English translations:")
    en_text = i18n.get_text("welcome_title", "en")
    print(f"    welcome_title: {en_text}")
    
    en_greeting = i18n.get_text("welcome_greeting", "en", name="John")
    print(f"    welcome_greeting: {en_greeting}")
    
    # Test Russian translations
    print("  Russian translations:")
    ru_text = i18n.get_text("welcome_title", "ru")
    print(f"    welcome_title: {ru_text}")
    
    ru_greeting = i18n.get_text("welcome_greeting", "ru", name="Иван")
    print(f"    welcome_greeting: {ru_greeting}")
    
    # Test fallback
    print("  Fallback testing:")
    fallback = i18n.get_text("nonexistent_key", "ru")
    print(f"    nonexistent_key: {fallback}")

def test_language_names():
    """Test language name functionality"""
    print("\n📝 Testing Language Names...")
    
    i18n = I18nManager()
    
    en_name = i18n.get_language_name("en")
    ru_name = i18n.get_language_name("ru")
    unknown_name = i18n.get_language_name("unknown")
    
    print(f"  English: {en_name}")
    print(f"  Russian: {ru_name}")
    print(f"  Unknown: {unknown_name}")

if __name__ == "__main__":
    print("🚀 Starting Multilingual Functionality Tests\n")
    
    test_language_detection()
    test_translations()
    test_language_names()
    
    print("\n✅ All tests completed!") 