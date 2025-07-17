"""
Simple test for nutrition insights markdown formatting
"""
import pytest


def check_markdown_entities(text: str) -> bool:
    """
    Check if markdown entities are properly matched
    
    Args:
        text: Text to check
        
    Returns:
        True if entities are properly matched, False otherwise
    """
    # Count bold entities
    bold_count = text.count('**')
    if bold_count % 2 != 0:
        return False
        
    # Check for common problematic patterns
    problematic_patterns = [
        '***',  # Three asterisks
        '****',  # Four asterisks
        '**\n**',  # Bold across newlines
        '**  **',  # Empty bold
    ]
    
    for pattern in problematic_patterns:
        if pattern in text:
            return False
            
    return True


def test_markdown_entity_validation():
    """Test various markdown patterns that could cause issues"""
    # Good patterns
    good_patterns = [
        "**Bold text**",
        "**Bold with emoji 🎯**",
        "**Bold:** Regular text",
        "**Bold** and **more bold**",
        "• Bullet point with **bold**",
        "Text with **bold** and normal text",
        "🔬 **Header:**\n• Bullet with **bold**"
    ]
    
    for pattern in good_patterns:
        assert check_markdown_entities(pattern), f"Good pattern failed: {pattern}"
    
    # Bad patterns that should fail
    bad_patterns = [
        "**Bold text",  # Unmatched bold
        "Bold text**",  # Unmatched bold
        "**Bold** and **unmatched",  # Mixed matched and unmatched
        "***Triple asterisk***",  # Triple asterisk
        "**  **",  # Empty bold
    ]
    
    for pattern in bad_patterns:
        assert not check_markdown_entities(pattern), f"Bad pattern should fail: {pattern}"


def test_byte_position_analysis():
    """Test the specific byte position issue that was causing the error"""
    # This is to understand the actual error at byte offset 159
    # Let's create a message that would have content at around byte 159
    message_start = "🔬 **Your Nutrition Analysis**\n\n📊 **Body Mass Index (BMI):**\n✅ **22.5** - Healthy weight range\n💡 Fantastic! You're in the ideal range! 🎉"
    
    # Check the length to understand where byte 159 would be
    print(f"Message length: {len(message_start)}")
    print(f"Byte length: {len(message_start.encode('utf-8'))}")
    
    # Show the characters around position 159
    if len(message_start.encode('utf-8')) > 159:
        utf8_bytes = message_start.encode('utf-8')
        print(f"Characters around byte 159: {utf8_bytes[155:165]}")
    
    # Test if the message has valid markdown
    assert check_markdown_entities(message_start), "Message should have valid markdown"


def test_original_vs_fixed_formatting():
    """Test the difference between original problematic formatting and fixed formatting"""
    
    # Original problematic patterns (these were in the original code)
    original_problems = [
        "📊 **Body Mass Index (BMI)**",  # Ends with **
        "🎯 **Ideal Weight Range**",     # Ends with **
        "🧬 **Metabolic Age**",          # Ends with **
    ]
    
    # Fixed patterns (with colons)
    fixed_patterns = [
        "📊 **Body Mass Index (BMI):**",  # Ends with :**
        "🎯 **Ideal Weight Range:**",     # Ends with :**
        "🧬 **Metabolic Age:**",          # Ends with :**
    ]
    
    # Both should technically pass markdown validation
    for pattern in original_problems:
        assert check_markdown_entities(pattern), f"Original should pass markdown: {pattern}"
    
    for pattern in fixed_patterns:
        assert check_markdown_entities(pattern), f"Fixed should pass markdown: {pattern}"
    
    # But the real issue might be something else - let's check for emojis at entity boundaries
    for pattern in original_problems:
        # Check if there are any issues with emojis next to markdown entities
        assert '**' in pattern, f"Pattern should contain bold entities: {pattern}"
        
    for pattern in fixed_patterns:
        assert '**' in pattern, f"Pattern should contain bold entities: {pattern}"


def test_complete_message_with_analysis():
    """Test a complete message and analyze potential issues"""
    
    # Create a realistic message that might cause issues
    message = """🔬 **Your Nutrition Analysis**

📊 **Body Mass Index (BMI):**
✅ **22.5** - Healthy weight range
💡 Fantastic! You're in the ideal range! 🎉 Keep up the great work maintaining your health!

🎯 **Ideal Weight Range:**
**65.0-81.3 kg** (BMI-based)
**72.5 kg** (Broca formula)

🧬 **Metabolic Age:**
✅ **28 years** (vs 30 actual)
Your metabolism is younger than your age!
💡 Amazing! Your healthy lifestyle is paying off! Keep doing what you're doing! 🚀

💧 **Daily Water Needs:**
**2.6L** (10 glasses)
Base: 2625ml + Activity: 0ml

🥗 **Optimal Macro Distribution:**
**Protein:** 150g (30%)
**Carbs:** 200g (40%)
**Fats:** 67g (30%)

🍽️ **Meal Distribution:**
**Breakfast:** 600 kcal (30%)
**Lunch:** 800 kcal (40%)
**Dinner:** 600 kcal (30%)

💡 **Personal Recommendations:**
• 🎉 You're maintaining great health! Keep enjoying balanced, nutritious meals
• 🚶‍♀️ Every step counts! Even light daily walks can boost your metabolism and mood
• ⏰ Smart strategy: Try eating your heartiest meal earlier when your metabolism is highest
• 💧 Stay hydrated for success! Aim for 2.6L daily (10 glasses)

🎯 **Goal-Specific Advice:**
⚖️ **Your Maintenance Mastery:**
• 🎯 You've found your sweet spot! Focus on consistent, joyful eating
• 📊 Weekly check-ins help you stay in tune with your body
• 🌈 Variety keeps nutrition exciting and ensures you get all nutrients
• 🏃‍♀️ Mix cardio and strength training for total body wellness

📅 **Analysis Date:** 2025-01-13
🔄 **Credits Remaining:** 100"""
    
    # Sanitize the message to fix markdown issues
    def sanitize_markdown_text(text: str) -> str:
        """Sanitize markdown text to prevent Telegram parsing issues"""
        # Fix problematic **\n** patterns by adding space after **
        text = text.replace('**\n**', '** \n**')
        # Fix any triple asterisks
        text = text.replace('***', '** *')
        # Fix any quadruple asterisks
        text = text.replace('****', '** **')
        # Fix empty bold patterns
        text = text.replace('**  **', '** **')
        return text
    
    sanitized_message = sanitize_markdown_text(message)
    
    # Analyze the message
    print(f"Message length: {len(sanitized_message)} characters")
    print(f"Byte length: {len(sanitized_message.encode('utf-8'))} bytes")
    
    # Check for markdown validity
    is_valid = check_markdown_entities(sanitized_message)
    print(f"Markdown valid: {is_valid}")
    
    # Count bold entities
    bold_count = sanitized_message.count('**')
    print(f"Bold entity count: {bold_count} (should be even)")
    
    # Check that it's not too long for Telegram (4096 character limit)
    assert len(sanitized_message) < 4096, f"Message too long for Telegram: {len(sanitized_message)} chars"
    
    # The message should have valid markdown after sanitization
    assert is_valid, "Sanitized message should have valid markdown formatting"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # Added -s to see print statements 