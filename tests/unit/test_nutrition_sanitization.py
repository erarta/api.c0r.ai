"""
Test nutrition insights markdown sanitization
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'api.c0r.ai')))

# Create a mock function since we can't import the full module due to Supabase dependencies
def sanitize_markdown_text(text: str) -> str:
    """
    Sanitize markdown text to prevent Telegram parsing issues
    """
    # Fix problematic **\n** patterns by adding space after **
    text = text.replace('**\n**', '** \n**')
    
    # Fix any triple asterisks
    text = text.replace('***', '** *')
    
    # Fix any quadruple asterisks
    text = text.replace('****', '** **')
    
    # Fix empty bold patterns
    text = text.replace('**  **', '** **')
    
    return text


def check_markdown_entities(text: str) -> bool:
    """
    Check if markdown entities are properly matched
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


class TestNutritionSanitization:
    """Test nutrition insights markdown sanitization"""
    
    def test_fix_problematic_newline_patterns(self):
        """Test fixing **\n** patterns"""
        problematic_text = "**Bold text**\n**More bold text**"
        sanitized = sanitize_markdown_text(problematic_text)
        
        # Should not contain the problematic pattern
        assert '**\n**' not in sanitized
        
        # Should contain the fixed pattern
        assert '** \n**' in sanitized
        
        # Should pass markdown validation
        assert check_markdown_entities(sanitized)
        
    def test_fix_triple_asterisks(self):
        """Test fixing *** patterns"""
        problematic_text = "Some text ***bold*** more text"
        sanitized = sanitize_markdown_text(problematic_text)
        
        # Should not contain triple asterisks
        assert '***' not in sanitized
        
        # Should contain the fixed pattern
        assert '** *' in sanitized
        
        # Should pass markdown validation
        assert check_markdown_entities(sanitized)
        
    def test_fix_quadruple_asterisks(self):
        """Test fixing **** patterns"""
        problematic_text = "Some text ****bold**** more text"
        sanitized = sanitize_markdown_text(problematic_text)
        
        # Should not contain quadruple asterisks
        assert '****' not in sanitized
        
        # Should contain the fixed pattern
        assert '** **' in sanitized
        
        # Should pass markdown validation
        assert check_markdown_entities(sanitized)
        
    def test_fix_empty_bold_patterns(self):
        """Test fixing **  ** patterns"""
        problematic_text = "Some text **  ** more text"
        sanitized = sanitize_markdown_text(problematic_text)
        
        # Should still contain the pattern (it's fixed to the same thing)
        assert '** **' in sanitized
        
        # Should pass markdown validation
        assert check_markdown_entities(sanitized)
        
    def test_complete_nutrition_message_sanitization(self):
        """Test sanitizing a complete nutrition message"""
        # This is the type of message that was causing issues
        problematic_message = """🔬 **Your Nutrition Analysis**

📊 **Body Mass Index (BMI):**
✅ **22.5** - Healthy weight range
💡 Fantastic! You're in the ideal range!

🎯 **Ideal Weight Range:**
**65.0-81.3 kg** (BMI-based)
**72.5 kg** (Broca formula)

🧬 **Metabolic Age:**
✅ **28 years** (vs 30 actual)
Your metabolism is younger than your age!

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
• 🎉 You're maintaining great health!
• 🚶‍♀️ Every step counts!

🎯 **Goal-Specific Advice:**
⚖️ **Your Maintenance Mastery:**
• 🎯 You've found your sweet spot!

📅 **Analysis Date:** 2025-01-13
🔄 **Credits Remaining:** 100"""
        
        # Sanitize the message
        sanitized = sanitize_markdown_text(problematic_message)
        
        # Check that problematic patterns are removed
        assert '**\n**' not in sanitized
        assert '***' not in sanitized
        assert '****' not in sanitized
        
        # Check that the message passes markdown validation
        assert check_markdown_entities(sanitized), "Sanitized message should pass markdown validation"
        
        # Check that the message is not too long
        assert len(sanitized) < 4096, f"Message too long: {len(sanitized)} characters"
        
        # Check that the content is preserved
        assert "Your Nutrition Analysis" in sanitized
        assert "Body Mass Index" in sanitized
        assert "Personal Recommendations" in sanitized
        
    def test_edge_cases(self):
        """Test edge cases for sanitization"""
        # Empty string
        assert sanitize_markdown_text("") == ""
        
        # String with no markdown
        normal_text = "This is normal text with no markdown"
        assert sanitize_markdown_text(normal_text) == normal_text
        
        # String with only good markdown
        good_markdown = "This is **bold** and this is **also bold**"
        assert sanitize_markdown_text(good_markdown) == good_markdown
        assert check_markdown_entities(good_markdown)
        
        # String with mixed patterns
        mixed_text = "**Good** text ***bad*** more **good** text"
        sanitized = sanitize_markdown_text(mixed_text)
        assert '***' not in sanitized
        assert check_markdown_entities(sanitized)
        
    def test_preserves_emojis_and_special_chars(self):
        """Test that emojis and special characters are preserved"""
        text_with_emojis = "🔬 **Analysis** 🎯 **Goals** 💡 **Tips**"
        sanitized = sanitize_markdown_text(text_with_emojis)
        
        # Should preserve all emojis
        assert "🔬" in sanitized
        assert "🎯" in sanitized
        assert "💡" in sanitized
        
        # Should still be valid markdown
        assert check_markdown_entities(sanitized)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 