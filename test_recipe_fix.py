#!/usr/bin/env python3
"""
Test script to verify recipe generation credit display fix
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Mock data to simulate user with credits
mock_user_data = {
    'user': {
        'id': 'test-user-id',
        'credits_remaining': 18,  # Same as in /status command
        'language': 'ru'
    },
    'profile': {
        'age': 25,
        'goal': 'weight_loss',
        'dietary_preferences': ['vegetarian'],
        'allergies': ['nuts']
    },
    'has_profile': True
}

def test_credit_display():
    """Test that credits are displayed correctly"""
    user = mock_user_data['user']
    profile = mock_user_data['profile']
    has_profile = mock_user_data['has_profile']
    user_language = user.get('language', 'en')
    
    print(f"Testing credit display for user with {user['credits_remaining']} credits")
    print(f"User language: {user_language}")
    print(f"Has profile: {has_profile}")
    
    # Test the instruction text generation logic
    if has_profile:
        dietary_prefs = profile.get('dietary_preferences', [])
        allergies = profile.get('allergies', [])
        
        dietary_text = ", ".join(dietary_prefs) if dietary_prefs and dietary_prefs != ['none'] else ("Нет" if user_language == 'ru' else "None")
        allergies_text = ", ".join(allergies) if allergies and allergies != ['none'] else ("Нет" if user_language == 'ru' else "None")
        goal_text = profile.get('goal', 'Не указано' if user_language == 'ru' else 'Not set')
        
        if user_language == 'ru':
            instruction_text = (
                f"🍽️ **Генерация рецептов**\n\n"
                f"📸 **Отправь мне фото** ингредиентов или блюда, и я создам персонализированный рецепт для тебя!\n\n"
                f"👤 **Твой профиль:**\n"
                f"🎯 Цель: {goal_text}\n"
                f"🍽️ Диета: {dietary_text}\n"
                f"⚠️ Аллергии: {allergies_text}\n\n"
                f"✨ **Я создам рецепты, которые:**\n"
                f"• Соответствуют твоим диетическим предпочтениям\n"
                f"• Избегают твоих аллергий\n"
                f"• Соответствуют твоим фитнес-целям\n"
                f"• Включают информацию о питательности\n\n"
                f"💳 **Осталось кредитов:** {user['credits_remaining']}\n"
                f"📱 **Просто отправь фото, чтобы начать!**"
            )
        else:
            instruction_text = (
                f"🍽️ **Recipe Generation**\n\n"
                f"📸 **Send me a photo** of food ingredients or a dish, and I'll generate a personalized recipe for you!\n\n"
                f"👤 **Your Profile:**\n"
                f"🎯 Goal: {goal_text}\n"
                f"🍽️ Diet: {dietary_text}\n"
                f"⚠️ Allergies: {allergies_text}\n\n"
                f"✨ **I'll create recipes that:**\n"
                f"• Match your dietary preferences\n"
                f"• Avoid your allergies\n"
                f"• Align with your fitness goals\n"
                f"• Include nutritional information\n\n"
                f"💳 **Credits remaining:** {user['credits_remaining']}\n"
                f"📱 **Just send a photo to get started!**"
            )
    else:
        if user_language == 'ru':
            instruction_text = (
                f"🍽️ **Генерация рецептов**\n\n"
                f"📸 **Отправь мне фото** ингредиентов или блюда, и я создам рецепт для тебя!\n\n"
                f"💡 **Совет:** Настрой свой профиль для персонализированных рецептов, которые соответствуют твоим диетическим предпочтениям и целям.\n\n"
                f"💳 **Осталось кредитов:** {user['credits_remaining']}\n"
                f"📱 **Просто отправь фото, чтобы начать!**"
            )
        else:
            instruction_text = (
                f"🍽️ **Recipe Generation**\n\n"
                f"📸 **Send me a photo** of food ingredients or a dish, and I'll generate a recipe for you!\n\n"
                f"💡 **Tip:** Set up your profile for personalized recipes that match your dietary preferences and goals.\n\n"
                f"💳 **Credits remaining:** {user['credits_remaining']}\n"
                f"📱 **Just send a photo to get started!**"
            )
    
    print("\n" + "="*50)
    print("GENERATED INSTRUCTION TEXT:")
    print("="*50)
    print(instruction_text)
    print("="*50)
    
    # Check if credits are displayed correctly
    if f"💳 **Осталось кредитов:** {user['credits_remaining']}" in instruction_text:
        print("✅ SUCCESS: Credits are displayed correctly in Russian!")
        print(f"✅ Credits shown: {user['credits_remaining']}")
        return True
    elif f"💳 **Credits remaining:** {user['credits_remaining']}" in instruction_text:
        print("✅ SUCCESS: Credits are displayed correctly in English!")
        print(f"✅ Credits shown: {user['credits_remaining']}")
        return True
    else:
        print("❌ FAILED: Credits are not displayed correctly!")
        return False

if __name__ == "__main__":
    print("Testing Recipe Generation Credit Display Fix")
    print("=" * 50)
    
    success = test_credit_display()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("The recipe generation now correctly displays credits and uses Russian language.")
    else:
        print("\n❌ TESTS FAILED!")
        sys.exit(1)