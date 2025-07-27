# 🌐 Multilingual Support for c0r.ai Bot

## Overview

The c0r.ai Telegram bot now supports multiple languages with automatic language detection and manual language switching. Currently supports **English** and **Russian** languages.

## Features

### ✅ Automatic Language Detection
- **Country-based detection**: Automatically detects Russian for users from:
  - 🇷🇺 Russia (RU)
  - 🇧🇾 Belarus (BY) 
  - 🇰🇿 Kazakhstan (KZ)
  - 🇰🇬 Kyrgyzstan (KG)
  - 🇦🇲 Armenia (AM)
  - 🇦🇿 Azerbaijan (AZ)
  - 🇬🇪 Georgia (GE)
  - 🇺🇿 Uzbekistan (UZ)

- **Phone number detection**: Detects Russian for phone numbers starting with:
  - `+7` (Russia)
  - `8` (Russia)
  - `+375` (Belarus)

### ✅ Manual Language Switching
- Users can change language via `/language` command
- Interactive language selection menu with flag emojis
- Language preference is saved in database

### ✅ Comprehensive Translations
- All bot messages, buttons, and error messages
- Welcome messages and help guides
- Status information and payment messages
- Rate limiting and error notifications

## Technical Implementation

### Database Schema

```sql
-- Added to users table
ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'en' CHECK (language IN ('en', 'ru'));
ALTER TABLE users ADD COLUMN country TEXT;
ALTER TABLE users ADD COLUMN phone_number TEXT;

-- Index for performance
CREATE INDEX idx_users_language ON users(language);
```

### Key Files

- **`api.c0r.ai/app/i18n.py`** - Main internationalization system
- **`api.c0r.ai/app/handlers/language.py`** - Language switching handlers
- **`migration_multilingual.sql`** - Database migration for multilingual support

### Language Detection Flow

1. **User starts bot** (`/start`)
2. **System detects language** based on:
   - Telegram `language_code` → country mapping
   - User's phone number patterns
   - Defaults to English if no match
3. **Language is saved** to database
4. **All messages** are displayed in detected language

### Translation System

```python
from handlers.i18n import i18n

# Get translated text
text = i18n.get_text("welcome_title", user_language)

# With parameters
greeting = i18n.get_text("welcome_greeting", user_language, name="John")
```

## Usage

### For Users

#### Automatic Detection
- Simply start the bot with `/start`
- Language is automatically detected and set
- All messages appear in your preferred language

#### Manual Language Change
1. Send `/language` command
2. Select your preferred language from the menu
3. Language is immediately changed and saved

### For Developers

#### Adding New Languages

1. **Add language enum**:
```python
class Language(Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    SPANISH = "es"  # New language
```

2. **Add translations**:
```python
def _load_translations(self):
    return {
        # ... existing languages
        Language.SPANISH.value: {
            "welcome_title": "🎉 **¡Bienvenido a c0r.ai Analizador de Comida!**",
            # ... more translations
        }
    }
```

3. **Update database migration**:
```sql
ALTER TABLE users ALTER COLUMN language DROP CONSTRAINT users_language_check;
ALTER TABLE users ADD CONSTRAINT users_language_check CHECK (language IN ('en', 'ru', 'es'));
```

#### Adding New Translation Keys

1. **Add to English translations** (base language):
```python
"new_feature_title": "🚀 **New Feature**",
"new_feature_desc": "This is a new feature with {parameter}",
```

2. **Add to Russian translations**:
```python
"new_feature_title": "🚀 **Новая функция**",
"new_feature_desc": "Это новая функция с {parameter}",
```

3. **Use in code**:
```python
title = i18n.get_text("new_feature_title", user_language)
desc = i18n.get_text("new_feature_desc", user_language, parameter="value")
```

## Testing

### Run Language Tests
```bash
python3 test_i18n_simple.py
```

### Test Coverage
- ✅ Language detection (country + phone)
- ✅ Translation system
- ✅ Fallback mechanisms
- ✅ Parameter formatting
- ✅ Language names

## Database Migration

### Apply Migration
```bash
# Connect to your Supabase database
psql "postgresql://postgres:[password]@[host]:5432/postgres"

# Run the migration
\i migration_multilingual.sql
```

### Migration Contents
- Adds `language`, `country`, `phone_number` columns to `users` table
- Creates index on `language` column for performance
- Updates `user_activity_summary` view to include language data
- Adds proper constraints and comments

## Version History

- **v0.4.0** - Initial multilingual support
  - English and Russian languages
  - Automatic language detection
  - Manual language switching
  - Comprehensive translations

## Future Enhancements

- [ ] Add more languages (Spanish, French, German)
- [ ] Language-specific payment currencies
- [ ] Regional content customization
- [ ] Language learning preferences
- [ ] Voice message language detection

## Support

For questions or issues with multilingual functionality:
- Check the test results: `python3 test_i18n_simple.py`
- Verify database migration: `migration_multilingual.sql`
- Review language detection logic in `i18n.py` 