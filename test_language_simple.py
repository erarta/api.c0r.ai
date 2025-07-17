#!/usr/bin/env python3
"""
Simple test script for language detection functionality
"""

import sys
import os
import re
from enum import Enum

# Add the app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'api.c0r.ai/app'))

# Mock logger to avoid dependency
class MockLogger:
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

# Import i18n with mocked logger
import sys
sys.modules['loguru'] = type('MockLoguru', (), {'logger': MockLogger()})

from i18n.i18n import i18n, Language

def test_language_detection():
    """Test language detection based on country and phone number"""
    print("🧪 Testing Language Detection")
    print("=" * 50)
    
    # Test cases: (country, phone, expected_language, description)
    test_cases = [
        # Russian-speaking countries
        ("RU", None, "ru", "Russia - should default to Russian"),
        ("BY", None, "ru", "Belarus - should default to Russian"),
        ("KZ", None, "ru", "Kazakhstan - should default to Russian"),
        ("KG", None, "ru", "Kyrgyzstan - should default to Russian"),
        ("AM", None, "ru", "Armenia - should default to Russian"),
        ("AZ", None, "ru", "Azerbaijan - should default to Russian"),
        ("GE", None, "ru", "Georgia - should default to Russian"),
        ("UZ", None, "ru", "Uzbekistan - should default to Russian"),
        
        # Phone number patterns
        (None, "+79001234567", "ru", "Russian phone +7 - should default to Russian"),
        (None, "89001234567", "ru", "Russian phone 8 - should default to Russian"),
        (None, "+375291234567", "ru", "Belarus phone +375 - should default to Russian"),
        
        # Other countries should default to English
        ("US", None, "en", "USA - should default to English"),
        ("GB", None, "en", "UK - should default to English"),
        ("DE", None, "en", "Germany - should default to English"),
        ("FR", None, "en", "France - should default to English"),
        ("IT", None, "en", "Italy - should default to English"),
        ("ES", None, "en", "Spain - should default to English"),
        ("CA", None, "en", "Canada - should default to English"),
        ("AU", None, "en", "Australia - should default to English"),
        
        # Other phone numbers should default to English
        (None, "+1234567890", "en", "US phone - should default to English"),
        (None, "+44123456789", "en", "UK phone - should default to English"),
        (None, "+49123456789", "en", "German phone - should default to English"),
        
        # Edge cases
        (None, None, "en", "No country/phone - should default to English"),
        ("", "", "en", "Empty strings - should default to English"),
        ("XX", "+1234567890", "en", "Unknown country - should default to English"),
    ]
    
    passed = 0
    failed = 0
    
    for country, phone, expected, description in test_cases:
        detected = i18n.detect_language(country, phone)
        status = "✅ PASS" if detected == expected else "❌ FAIL"
        
        if detected == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | Country: {country or 'None'}, Phone: {phone or 'None'} -> {detected} (expected: {expected})")
        print(f"    {description}")
        print()
    
    print(f"📊 Results: {passed} passed, {failed} failed")
    return failed == 0

def test_translations():
    """Test translation functionality"""
    print("🌐 Testing Translations")
    print("=" * 50)
    
    # Test basic translations
    test_keys = [
        "welcome_title",
        "btn_analyze_food", 
        "btn_main_menu",
        "error_general"
    ]
    
    passed = 0
    failed = 0
    
    for key in test_keys:
        # Test English
        en_text = i18n.get_text(key, "en")
        if en_text and not en_text.startswith("[Missing"):
            print(f"✅ English '{key}': {en_text[:50]}...")
            passed += 1
        else:
            print(f"❌ English '{key}': {en_text}")
            failed += 1
        
        # Test Russian
        ru_text = i18n.get_text(key, "ru")
        if ru_text and not ru_text.startswith("[Missing"):
            print(f"✅ Russian '{key}': {ru_text[:50]}...")
            passed += 1
        else:
            print(f"❌ Russian '{key}': {ru_text}")
            failed += 1
        
        print()
    
    # Test parameter formatting
    try:
        greeting_en = i18n.get_text("welcome_greeting", "en", name="John")
        greeting_ru = i18n.get_text("welcome_greeting", "ru", name="Иван")
        
        if "John" in greeting_en and "Иван" in greeting_ru:
            print("✅ Parameter formatting works correctly")
            passed += 1
        else:
            print("❌ Parameter formatting failed")
            failed += 1
    except Exception as e:
        print(f"❌ Parameter formatting error: {e}")
        failed += 1
    
    print(f"📊 Translation Results: {passed} passed, {failed} failed")
    return failed == 0

def test_language_names():
    """Test language name functionality"""
    print("📝 Testing Language Names")
    print("=" * 50)
    
    en_name = i18n.get_language_name("en")
    ru_name = i18n.get_language_name("ru")
    unknown_name = i18n.get_language_name("xx")
    
    print(f"English name: {en_name}")
    print(f"Russian name: {ru_name}")
    print(f"Unknown language: {unknown_name}")
    
    if en_name == "English" and ru_name == "Русский" and unknown_name == "Unknown":
        print("✅ Language names work correctly")
        return True
    else:
        print("❌ Language names failed")
        return False

if __name__ == "__main__":
    print("🚀 Starting Language Detection Tests")
    print("=" * 60)
    print()
    
    # Run all tests
    test1_passed = test_language_detection()
    print()
    
    test2_passed = test_translations()
    print()
    
    test3_passed = test_language_names()
    print()
    
    # Summary
    print("=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    if test1_passed and test2_passed and test3_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Language detection works correctly")
        print("✅ Translations are complete")
        print("✅ Language names are correct")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        if not test1_passed:
            print("❌ Language detection has issues")
        if not test2_passed:
            print("❌ Translation system has issues")
        if not test3_passed:
            print("❌ Language names have issues")
        sys.exit(1) 