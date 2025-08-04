# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-01-30

### 🔧 Bug Fixes
- **Telegram Entity Parsing Error**: Fixed "Missing format parameter 'progress_bar' for key 'daily_progress' in language ru" error by resolving translation key conflicts between `daily_progress` and `nutrition_daily_progress` keys
- **Language-Aware Formatting**: Replaced hardcoded Russian characters ("г", "ккал") with i18n calls in `format_analysis_result` to ensure language-aware formatting
- **Translation Key Separation**: Created separate `nutrition_daily_progress` key for nutrition analysis to avoid conflicts with daily progress tracking
- **Pydantic v2 Compatibility**: Updated all models to use `pattern` instead of `regex` in Field definitions for Pydantic v2 compatibility
- **Test Infrastructure Fixes**: Fixed import paths, mocking strategies, and assertion updates for comprehensive test coverage
- **Unit Test Coverage**: Fixed 97 unit tests across commands, health checks, shared models, and nutrition calculations
- **Import Path Corrections**: Updated import paths to reflect current project structure
- **Test Mocking**: Corrected mock targets and parameters for external dependencies
- **Validation Error Handling**: Updated test expectations for Pydantic v2 validation errors

### ⚠️ Deployment Note
- **Production Deployment Required**: The Telegram entity parsing error fix requires deployment to production environment. The local code changes are correct, but the production environment may still be running the old code causing the "Missing format parameter 'progress_bar' for key 'daily_progress' in language ru" error.

### 📝 Technical Details
- **Files Modified**: 
  - `services/api/bot/handlers/photo.py` - Updated to use `nutrition_daily_progress` key
  - `i18n/en/nutrition.py` - Added `nutrition_daily_progress` translation
  - `i18n/ru/nutrition.py` - Added `nutrition_daily_progress` translation
  - All Pydantic model files - Updated `regex` to `pattern`
  - All test files - Fixed imports, mocks, and assertions
- **Translation Keys**: Separated `daily_progress` (for daily tracking) from `nutrition_daily_progress` (for nutrition analysis)
- **Test Results**: All 97 unit tests passing, integration tests require environment variables

---

## Archive

For older changelog entries, see the organized files in the [`changelogs/`](changelogs/) directory:

- [`changelogs/v0.3.x.md`](changelogs/v0.3.x.md) - Version 0.3.x changes (0.3.0 - 0.3.68)
- [`changelogs/v0.2.x.md`](changelogs/v0.2.x.md) - Version 0.2.x changes  
- [`changelogs/v0.1.x.md`](changelogs/v0.1.x.md) - Version 0.1.x changes
- [`changelogs/v0.0.x.md`](changelogs/v0.0.x.md) - Version 0.0.x changes

## Contributing

When adding new changes:
1. Add entries directly to the appropriate version file in `changelogs/` directory
2. Keep the main `CHANGELOG.md` clean - only update archive links when needed
3. Follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format
4. Use categories: Added, Changed, Deprecated, Removed, Fixed, Security

## [v0.4.0] - 2025-01-26

### ✨ Added
- **Dynamic Motivational Messages**: Implemented random message variants to eliminate repetitive messages during profile setup
- **10 variants** for step progress messages (e.g., "Шаг за шагом к твоему идеальному профилю!", "Каждый шаг приближает тебя к цели!")
- **5 variants each** for important tips, restart tips, dietary tips, and allergy tips
- New motivational messages utility (`services/api/bot/utils/motivational_messages.py`) with functions:
  - `get_profile_step_message()` - Random step progress messages
  - `get_random_important_tip()` - Random important tips
  - `get_random_restart_tip()` - Random restart tips  
  - `get_random_dietary_tip()` - Random dietary tips
  - `get_random_allergies_tip()` - Random allergy tips
- **Docker Compose Override** for development (`docker-compose.override.yml`) with volume mounting
- **Quick translation update script** (`scripts/update-translations.sh`) for instant updates without rebuilds
- Missing Russian translations:
  - `profile_allergy_sesame`: "🌰 Кунжут"
  - `profile_allergy_sulfites`: "🧪 Сульфиты" 
  - `profile_setup_important`: "💡 Это важно для персональных рекомендаций!"
  - `profile_setup_restart`: "📝 Ты всегда можешь перезапустить настройку профиля в любое время!"
  - `profile_setup_step`: "🔄 Шаг за шагом к твоему идеальному профилю!"
  - `profile_setup_goal_success`: "Фантастика! Твоя цель установлена - вперед к успеху! 🚀"
  - `profile_setup_dietary_tip`: "💡 Чем больше ты мне расскажешь, тем лучше я смогу помочь тебе с персональными советами!"
  - `profile_setup_allergies_tip`: "💡 Я буду следить за этим во всех моих рекомендациях - твоя безопасность превыше всего!"
  - `profile_summary`: "📋 **Твой потрясающий профиль:**"
  - `profile_diet`: "🥗 Диетические предпочтения: {diet}"
  - `profile_allergies`: "⚠️ Аллергии: {allergies}"
  - `profile_ready`: "🎉 **Все готово! Теперь я могу дать тебе персональные рекомендации, которые помогут тебе достичь твоих потрясающих целей!**"

### 🐛 Fixed
- **Eliminated duplicate emojis** in profile setup flow (e.g., `💡 💡` → `💡`)
- **Removed repetitive motivational messages** that appeared on every step
- Fixed missing `profile_setup_activity` message display in weight→activity transition
- Improved profile setup flow with proper message progression

### ⚡ Improved  
- **User Experience**: Every profile setup step now shows varied, engaging messages
- **Developer Experience**: Instant translation updates with volume mounting (2-5 seconds vs 2-5 minutes rebuild)
- **Maintainability**: Modular system for adding new message variants
- **Performance**: Fast iteration cycles for translation changes

### 📚 Documentation
- Added comprehensive guide: `docs/development/translation-quick-updates.md`
- Created development script: `scripts/update-translations.sh`
- Updated volume mounting setup for faster development

### 🔧 Technical
- Enhanced profile handler (`services/api/bot/handlers/profile.py`) to use random message selection
- Added translation variant arrays in `i18n/ru/profile.py`
- Implemented fallback mechanism for missing variants
- Maintained backward compatibility with existing translation keys

---
