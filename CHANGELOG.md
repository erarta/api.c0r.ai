# Changelog

All notable changes to this project will be documented in this file.

## [0.3.61] - 2025-07-20

### Fixed
- **Callback Query Timeout**: Fixed TelegramBadRequest "query is too old and response timeout expired" error in profile setup process
- **Callback Answer Error Handling**: Added try-catch blocks around all `callback.answer()` calls to handle expired callback queries gracefully
- **Profile Setup Stability**: Improved error handling in `complete_profile_setup`, `process_allergies`, and other callback handlers
- **User Experience**: Users no longer see errors when callback queries expire during profile setup

## [0.3.60] - 2025-07-20

### Fixed
- **Profile Setup Error Handling**: Fixed UnboundLocalError in `complete_profile_setup` function caused by missing `user_language` variable in exception handling blocks
- **Exception Block Variable Scope**: Added proper `user_language` initialization in `except ValueError` and `except Exception` blocks
- **Profile Setup Flow**: Ensured consistent variable scope throughout the profile setup process including all error handling paths
- **Test Suite**: Verified core nutrition calculation and formatting tests pass successfully

## [0.3.59] - 2025-07-20

### Fixed
- **Profile Setup Error Handling**: Fixed UnboundLocalError in `complete_profile_setup` function caused by duplicate `user_language` variable definitions in exception handling blocks
- **Exception Block Variable Scope**: Removed duplicate `user_language` definitions in `except ValueError` and `except Exception` blocks
- **Profile Setup Flow**: Ensured consistent variable scope throughout the profile setup process including error handling

## [0.3.58] - 2025-07-20

### Fixed
- **Profile Setup Variable Scope**: Fixed UnboundLocalError in `process_dietary_preferences` function caused by duplicate `user_language` variable definition
- **Variable Scope Conflict**: Removed duplicate `user_language` definition in the `diet_done` block that was causing variable scope conflicts
- **Profile Setup Flow**: Ensured consistent variable scope throughout the profile setup process

## [0.3.57] - 2025-07-20

### Fixed
- **Profile Setup Completion Error**: Fixed UnboundLocalError in `complete_profile_setup` function where `user_language` variable was not defined at the beginning of the function
- **Profile Setup Flow**: Moved `user_language` initialization to the start of `complete_profile_setup` to ensure it's available throughout the function
- **Profile Setup Error Handling**: Removed duplicate `user_language` definitions and streamlined error handling in profile completion process

## [0.3.56] - 2025-07-20

### Fixed
- **Profile Display Enhancement**: Added dietary preferences and allergies information to profile display
- **Profile Display Translation**: All profile fields now show translated values instead of English codes
- **Profile Display Format**: Fixed duplicate emojis and units in profile display (e.g., "👨 👨 Мужской", "170 см см")
- **Macro Distribution Error**: Fixed KeyError 'protein_g' in nutrition section by correcting data structure access
- **Payment Service Error**: Added proper error handling for ServerDisconnectedError in payment processing
- **Payment Error Translation**: Added Russian translation for payment service unavailable message
- **Dietary Preferences Error**: Fixed UnboundLocalError in `process_dietary_preferences` function
- **Profile Completion Translation**: Fixed NameError in `process_allergies` function where `user_language` variable was not defined
- **Final Profile Message**: Completely translated the profile setup completion message to Russian
- **Profile Summary Translation**: All profile summary fields now use proper Russian translations:
  - Age, Height, Weight, Activity, Goal, Diet, Allergies
  - Daily calorie target message
  - Completion status messages
- **Profile Completion Buttons**: Translated all 4 buttons in the final profile setup screen:
  - "📊 Посмотреть дневной план" (View Daily Plan)
  - "🍕 Анализировать еду" (Analyze Food)
  - "🍽️ Получить рецепт" (Get Recipe)
  - "🏠 Главное меню" (Main Menu)
- **Dietary Preferences Translation**: Added comprehensive Russian translations for all dietary preferences:
  - Vegetarian, Vegan, Pescatarian, Keto, Paleo, Mediterranean
  - Low Carb, Low Fat, Gluten Free, Dairy Free, Halal, Kosher
- **Allergies Translation**: Added comprehensive Russian translations for all allergies:
  - Nuts, Peanuts, Shellfish, Fish, Eggs, Dairy, Soy, Wheat, Gluten, Sesame, Sulfites
- **Profile Display Enhancement**: Added dietary preferences and allergies sections to profile display with proper translations

### Added
- **Profile Display Sections**: Added dedicated sections for dietary preferences and allergies in profile display
- **Translation Keys**: Added new translation keys for profile display enhancements
- **Error Handling**: Enhanced error handling for payment service connectivity issues

## [0.3.55] - 2025-07-20

### Fixed
- **Profile Completion Translation**: Fixed NameError in `process_allergies` function where `user_language` variable was not defined
- **Final Profile Message**: Completely translated the profile setup completion message to Russian
- **Profile Summary Translation**: All profile summary fields now use proper Russian translations:
  - Age, Height, Weight, Activity, Goal, Diet, Allergies
  - Daily calorie target message
  - Completion status messages
- **Profile Completion Buttons**: Translated all 4 buttons in the final profile setup screen:
  - "📊 Посмотреть дневной план" (View Daily Plan)
  - "🍕 Анализировать еду" (Analyze Food)
  - "🍽️ Получить рецепт" (Get Recipe)
  - "🏠 Главное меню" (Main Menu)
- **Dietary Preferences Translation**: Added comprehensive Russian translations for all dietary preferences:
  - Vegetarian, Vegan, Pescatarian, Keto, Paleo, Mediterranean
  - Low Carb, Low Fat, Gluten Free, Dairy Free, Halal, Kosher
- **Allergies Translation**: Added comprehensive Russian translations for all allergies:
  - Nuts, Peanuts, Shellfish, Fish, Eggs, Dairy, Soy, Wheat, Gluten, Sesame, Sulfites

### Added
- **Translation Keys**: Added new translation keys for profile completion and dietary information
- **Profile Completion Flow**: Enhanced profile completion with comprehensive Russian translations

## [0.3.54] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed UnboundLocalError in `process_age` and `process_goal` functions where `user_language` variable was not defined
- **Telegram Markdown Error**: Fixed TelegramBadRequest "can't parse entities" error by removing `parse_mode="Markdown"` from messages containing emojis
- **Profile Setup Flow**: Ensured all profile setup steps use proper Russian translations with emoji support
- **Gender Selection**: Fixed gender selection step with proper Russian translations and emoji display
- **Activity Level Selection**: Enhanced activity level descriptions with detailed Russian translations
- **Goal Selection**: Improved goal selection step with clear Russian translations and emoji indicators
- **Dietary Preferences**: Enhanced dietary preferences step with comprehensive Russian translations and emoji indicators
- **Allergies Selection**: Improved allergies selection step with clear Russian translations and emoji indicators

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for all profile setup steps
- **Emoji Support**: Added emoji indicators for better user experience in profile setup
- **Error Handling**: Improved error handling for Telegram message formatting issues

## [0.3.53] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in 8-step profile setup process
- **Gender Selection**: Improved clarity and completeness of gender selection translations
- **Allergies Translation**: Enhanced allergies selection with better Russian translations
- **Dietary Preferences**: Improved dietary preferences selection with comprehensive Russian translations
- **Profile Setup Flow**: Enhanced overall profile setup flow with better user experience

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup steps
- **User Experience**: Improved clarity and completeness of all profile setup messages

## [0.3.52] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Translation**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.51] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Translation**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.50] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Translation**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.49] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Translation**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.48] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Translation**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.47] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Translation**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.46] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Translation**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.45] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Translation**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.44] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Translation**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.43] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Translation**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.42] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Translation**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.41] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Translation**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.40] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.39] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.38] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.37] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.36] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.35] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.34] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.33] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.32] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.31] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.30] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.29] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.28] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.27] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.26] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.25] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.24] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.23] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.22] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.21] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.20] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.19] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.18] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.17] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.16] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.15] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.14] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.13] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.12] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.11] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.10] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.9] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.8] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.7] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.6] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.5] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.4] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.3] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.2] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.1] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.3.0] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.2.9] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.2.8] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.2.7] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.2.6] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.2.5] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.2.4] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.2.3] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.2.2] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.2.1] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.2.0] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.1.9] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.1.8] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.1.7] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.1.6] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.1.5] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.1.4] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.1.3] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.1.2] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.1.1] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.1.0] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.0.9] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.0.8] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.0.7] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.0.6] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.0.5] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.0.4] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.0.3] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.0.2] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.0.1] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup

## [0.0.0] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed translation issues in profile setup process
- **Gender Selection**: Improved gender selection translations
- **Allergies Selection**: Enhanced allergies selection translations
- **Dietary Preferences**: Improved dietary preferences translations

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for profile setup
