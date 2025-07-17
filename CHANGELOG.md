# Changelog

All notable changes to this project will be documented in this file.

## [0.3.26] - 2025-01-21

### Added
- **I18n Folder Structure Refactoring**: Moved all i18n-related files to dedicated `/i18n` folder for better organization
- **Separate Translation Files**: Split translations into separate `en.py` and `ru.py` files for easier maintenance
- **Clean Import Structure**: Updated all imports to use absolute paths from the new i18n folder

### Changed
- **File Organization**: Moved `i18n.py`, `ru.py`, and `en.py` from `api.c0r.ai/app/handlers/` to `/i18n/` folder
- **Import Paths**: Updated all handler files to use `from i18n.i18n import i18n` instead of relative imports
- **Translation Management**: Separated English and Russian translations into individual files for better maintainability
- **Code Structure**: Improved code organization with dedicated i18n module structure

### Fixed
- **Import Consistency**: Eliminated all relative imports of i18n system across the codebase
- **Module Path Issues**: Resolved import path conflicts and module resolution issues
- **Code Organization**: Improved maintainability with better file structure and organization

### Technical
- **Folder Structure**: Created dedicated `/i18n` folder for all internationalization files
- **Import Updates**: Updated imports in all handler files (`commands.py`, `language.py`, `nutrition.py`, `profile.py`, `daily.py`, `photo.py`, `keyboards.py`)
- **System Integration**: Updated imports in `bot.py`, `common/nutrition_calculations.py`, and test files
- **Translation Separation**: Split monolithic translation dictionary into separate language files
- **Code Cleanup**: Removed old i18n folder structure and cleaned up import paths

### User Experience
- **No Functional Changes**: All existing functionality remains exactly the same
- **Improved Maintainability**: Better code organization for future translation updates
- **Cleaner Architecture**: More organized codebase structure for internationalization

### Testing
- **I18n Tests**: All i18n functionality tests pass (language detection, translations, fallbacks)
- **Language Tests**: All language detection tests pass (25/25 tests passed)
- **Import Validation**: All import paths work correctly with new folder structure
- **Functionality Verification**: All bot features work correctly with new i18n structure

## [0.3.25] - 2025-01-21

### Added
- **Consistent Back Button Navigation**: Replaced "Main Menu" buttons with "⬅️ Назад" buttons across all major sections
- **Unified Navigation Experience**: Standardized back button usage in status, buy credits, and water tracker sections
- **Simplified User Interface**: Streamlined navigation with consistent back button pattern

### Changed
- **Status Section Navigation**: Replaced "Main Menu" button with "⬅️ Назад" button in account status display
- **Buy Credits Navigation**: Updated buy credits section to use back button instead of main menu
- **Water Tracker Navigation**: Replaced main menu button with back button in water tracking interface
- **Navigation Consistency**: All major sections now use consistent back button navigation pattern

### Fixed
- **Navigation Flow**: Improved user navigation flow across all bot sections with simplified button structure
- **Interface Consistency**: Eliminated mixed navigation patterns for better user experience
- **Button Clarity**: Removed potential confusion from inconsistent button labeling

### Technical
- **Keyboard Standardization**: Unified keyboard creation across all major sections
- **Navigation Pattern**: Established consistent back button pattern throughout the application
- **Code Consistency**: Standardized button creation and callback handling

### User Experience
- **Consistent Navigation**: Users experience consistent back button navigation across all sections
- **Simplified Interface**: Cleaner, more intuitive navigation with single back button
- **Reduced Cognitive Load**: Users no longer need to remember different navigation patterns

### Testing
- **Unit Tests Validation**: All nutrition calculation tests pass (39/39)
- **Formatting Tests**: All nutrition formatting tests pass (4/4)
- **Sanitization Tests**: All nutrition sanitization tests pass (4/4)
- **Language Detection Tests**: All language detection tests pass (25/25)
- **Translation Tests**: All translation tests pass (9/9)
- **I18n Tests**: All i18n functionality tests pass
- **Syntax Validation**: All modified files compile without errors
- **Import Validation**: All function imports remain intact

## [0.3.24] - 2025-01-21

### Added
- **Simplified Daily Plan Navigation**: Replaced all buttons in daily plan with single "⬅️ Назад" button for cleaner interface
- **Consistent Back Navigation**: Added back buttons to weekly progress and meal history views for seamless navigation
- **Streamlined User Experience**: Simplified daily plan interface to focus on information display rather than multiple action buttons

### Changed
- **Daily Plan Interface**: Removed multiple action buttons (Add Meal, Weekly Progress, Edit Profile, Meal History, Main Menu) from daily plan
- **Navigation Consistency**: All daily plan related views now use consistent back button navigation
- **User Interface Simplification**: Daily plan now shows only essential information with single back button

### Fixed
- **Navigation Flow**: Improved user navigation flow in daily plan section with simplified button structure
- **Interface Clarity**: Removed potential confusion from multiple button options in daily plan display

### Technical
- **Keyboard Simplification**: Streamlined keyboard creation in daily plan functions
- **Navigation Consistency**: Standardized back button usage across daily plan related functions
- **Code Cleanup**: Removed unused button handlers and simplified callback structure

### User Experience
- **Cleaner Interface**: Daily plan now has cleaner, less cluttered interface
- **Simplified Navigation**: Users can easily return to main menu with single back button
- **Focused Information Display**: Daily plan focuses on displaying nutrition information rather than multiple action options

## [0.3.23] - 2025-01-21

### Added
- **Complete Calorie Unit Localization**: Full Russian translation of "Weekly Progress Summary" section
- **Enhanced Daily Progress Localization**: Complete Russian translation of daily progress display in photo analysis
- **Comprehensive Unit Standardization**: Replaced all "cal" units with "kcal" throughout the application
- **Back Button for Analyze Info**: Added "⬅️ Назад" button to "How to Analyze Food Photos" section for easy navigation
- **Complete Buy Credits Localization**: Full Russian translation of all buy credits sections including buttons and payment plans
- **Enhanced I18n System**: Added 20+ new translation keys for complete localization coverage
- **Status Symbols Explanation**: Added clear explanation of nutrition status symbols (⚠️ low, 🟡 medium, ✅ good, 🔴 exceeded)
- **Credits Explanation**: Added comprehensive explanation of what credits are and how they work (1 credit = 1 photo analysis)
- **Back Button in Nutrition Insights**: Replaced "Main Menu" button with "⬅️ Назад" button in nutrition analysis results

### Changed
- **BREAKING**: Replaced all "cal" units with "kcal" for consistency across the application
- **English Localization**: Updated English localization to use "kcal" instead of "cal"
- **Russian Localization**: Updated Russian localization to use "ккал" instead of "cal"
- **Photo Analysis Results**: Enhanced photo analysis result formatting with proper i18n support
- **Daily Progress Display**: Improved daily progress display with localized units and labels
- **Weekly Progress Summary**: Complete Russian translation including units and meal counts
- **Analyze Info Navigation**: Added back button to return to main menu from analyze info section
- **Buy Credits Interface**: Complete localization of all buy credits text, buttons, and payment plan descriptions
- **Photo Analysis Credits**: Localized all credit-related messages in photo analysis results
- **Payment Plan Display**: Fixed hardcoded "за" preposition to use proper i18n localization
- **Nutrition Insights Navigation**: Improved user experience with back button instead of main menu
- **Help Section Enhancement**: Added detailed credits explanation in help section
- **Daily Plan Enhancement**: Added status symbols explanation for better user understanding

### Fixed
- **Unit Consistency**: Ensured all calorie displays use consistent "kcal" format
- **Localization Coverage**: Added missing i18n keys for daily progress section
- **Photo Analysis Formatting**: Fixed hardcoded unit displays in photo analysis results
- **Navigation Flow**: Improved user navigation with back button in analyze info section
- **Buy Credits Hardcoded Text**: Replaced all hardcoded English text in buy credits with proper i18n keys
- **Out of Credits Messages**: Localized all out of credits messages in photo analysis
- **Payment Plan Prepositions**: Fixed hardcoded Russian preposition "за" to use i18n system
- **Credit Display Messages**: Localized "Credits Remaining" text throughout the application
- **Hardcoded "Edit Profile"**: Fixed hardcoded "Edit Profile" text in daily plan to use i18n
- **Hardcoded "Main Menu"**: Fixed all hardcoded "Main Menu" text to use i18n keys
- **Status Symbols Clarity**: Added explanation for nutrition status symbols to prevent user confusion
- **Credits Understanding**: Added clear explanation of credit system to help users understand the pricing model

### Technical
- **Test Data Updates**: Updated test data to use "kcal" instead of "cal" for consistency
- **Code Comments**: Improved code comments to use "kcal" instead of "cal"
- **Photo Handler Enhancement**: Enhanced photo.py to use i18n for all unit displays
- **I18n Key Expansion**: Added new translation keys for daily progress and weekly summary
- **Keyboard Enhancement**: Added back button functionality to analyze info callback handler
- **Buy Credits Localization**: Added comprehensive i18n keys for all buy credits functionality
- **Payment System Integration**: Enhanced payment plan display with proper localization
- **Database Key Alignment**: Ensured consistent key names throughout data pipeline
- **Navigation System**: Improved navigation consistency across all bot sections
- **Error Handling**: Enhanced error handling with proper localized back buttons

### User Experience
- **Consistent Unit Display**: All calorie values now display with proper "kcal" units
- **Fully Localized Weekly Summary**: Russian users see complete Russian translation of weekly progress
- **Enhanced Daily Progress**: Photo analysis results now show localized daily progress information
- **Professional Localization**: All unit displays properly translated and formatted
- **Improved Navigation**: Users can easily return to main menu from analyze info section
- **Complete Buy Credits Experience**: Russian users see fully localized buy credits interface
- **Seamless Payment Flow**: All payment plan descriptions and buttons properly translated
- **Consistent Language Experience**: No more mixed language content in any bot interaction
- **Clear Status Understanding**: Users now understand what nutrition status symbols mean
- **Transparent Credit System**: Users clearly understand that 1 credit = 1 photo analysis
- **Intuitive Navigation**: Back buttons provide consistent navigation experience

### Testing
- **Unit Tests Validation**: All nutrition calculation tests pass (39/39)
- **Formatting Tests**: All nutrition formatting tests pass (4/4)
- **Sanitization Tests**: All nutrition sanitization tests pass (7/7)
- **Simple Sanitization Tests**: All simple sanitization tests pass (4/4)
- **Test Data Consistency**: Updated all test data to use "kcal" instead of "cal"
- **Localization Testing**: Verified all new i18n keys work correctly
- **Navigation Testing**: Confirmed back button functionality works properly
- **Credits Explanation Testing**: Verified credits explanation displays correctly
- **Status Symbols Testing**: Confirmed status symbols explanation works properly

## [0.3.22] - 2025-01-21

### Added
- **Complete Currency Localization**: Replaced all "RUB" currency displays with "Р" symbol for Russian users
- **Full Nutrition Analysis Localization**: Complete Russian translation of nutrition analysis output including:
  - All units: `g` → `гр`, `kg` → `кг`, `ml` → `мл`, `L` → `л`, `cal` → `ккал`
  - All labels: `years` → `лет`, `actual` → `фактический`, `base` → `базовый уровень`
  - All formulas: `BMI-based` → `по ИМТ`, `Broca formula` → `по формуле Брока`
  - All status indicators: `glasses` → `стаканов`
- **Complete Profile Localization**: Full Russian translation of profile display including:
  - Profile title: "👤 **Мой профиль**"
  - All field names: Age, Gender, Height, Weight, Activity Level, Goal
  - All values: Male/Female, activity levels, goals, units
  - Back button with arrow: "⬅️ Назад"
- **Enhanced i18n System**: Added 50+ new translation keys for nutrition units, profile fields, and UI elements

### Changed
- **Currency Display**: All payment plans and price displays now use "Р" instead of "RUB"
- **Nutrition Analysis Output**: All nutrition analysis now fully localized with proper Russian units and labels
- **Profile Interface**: Complete profile display now uses i18n for all text elements
- **Buy Command**: Payment plan displays now use user's language preference
- **Daily Plan**: Nutrition breakdown section now fully localized with Russian macro names

### Fixed
- **Critical Protein Data Bug**: Fixed critical issue where protein data (0.0g) was not displaying correctly in daily plan
  - **Root Cause**: Key name mismatch between ML service (`proteins`) and database extraction (`protein`)
  - **Solution**: Updated `get_daily_calories_consumed()` to use correct keys: `proteins`, `carbohydrates`
  - **Impact**: Protein values now correctly display (e.g., 25.5г instead of 0.0г)
- **Data Extraction Consistency**: Fixed key name inconsistencies across the entire data pipeline
- **Language Consistency**: Eliminated all hardcoded English text in Russian user interface
- **Profile Display**: Fixed profile information display to use proper language-specific formatting

### Technical
- **Database Key Alignment**: Fixed key name mismatches between ML service response and database extraction
- **Enhanced Logging**: Added comprehensive debug logging for nutrition data extraction
- **I18n Key Expansion**: Added extensive new translation keys for complete localization
- **Data Pipeline Validation**: Ensured consistent key names throughout data flow
- **Error Prevention**: Added validation to prevent similar key name mismatches in future

### User Experience
- **Fully Localized Interface**: Russian users now see complete Russian interface with proper units
- **Accurate Nutrition Data**: Protein, fats, and carbs now display correct values from food analysis
- **Consistent Currency**: All prices display with "Р" symbol for Russian users
- **Professional Localization**: All text elements properly translated and formatted
- **Seamless Experience**: No more mixed language content or incorrect data display

### Database
- **Data Extraction Fix**: Fixed protein and carbohydrate data extraction from kbzhu field
- **Logging Enhancement**: Added detailed logging for nutrition data processing
- **Key Name Standardization**: Ensured consistent key names across all data operations

### Testing
- **Data Pipeline Validation**: Verified correct data extraction from ML service to database
- **Localization Testing**: Confirmed all new translation keys work correctly
- **Currency Display Testing**: Verified "Р" symbol displays correctly in all contexts
- **Profile Localization Testing**: Confirmed complete profile translation functionality

## [0.3.21] - 2025-01-21

### Added
- **Complete Test Suite Overhaul**: All tests now pass 100% with comprehensive coverage
- **I18n Test Integration**: Updated all tests to work with new i18n-based implementation
- **Language Parameter Support**: All test functions updated to handle language parameters
- **Mock System Enhancement**: Comprehensive mock setup for i18n system and database calls
- **Test Coverage Validation**: Verified all critical functionality with updated test expectations

### Changed
- **Test Function Signatures**: Updated all test functions to match new i18n-based signatures
- **Expected Outputs**: Updated all test assertions to match new localized text outputs
- **Mock Configurations**: Enhanced mock setups to properly simulate i18n system behavior
- **Async Test Handling**: Fixed async/await patterns in all test functions
- **Error Handler Testing**: Updated error handler tests to match new callback behavior

### Fixed
- **Test Import Issues**: Resolved import errors caused by absolute imports in test environment
- **Zero Division Errors**: Fixed BMI calculation tests to handle edge cases properly
- **Callback Query Testing**: Fixed callback query tests to match new i18n implementation
- **Mock Return Values**: Updated all mock return values to match new function signatures
- **Test Assertions**: Fixed all test assertions to match new localized text outputs
- **Error Handler Callbacks**: Fixed error handler test expectations for callback.answer() calls

### Technical
- **Test Infrastructure**: Complete overhaul of test infrastructure for i18n compatibility
- **Mock System**: Enhanced mock system to properly simulate i18n translations
- **Coverage Validation**: All tests now properly validate i18n-based functionality
- **Error Handling**: Updated error handling tests to match new implementation patterns
- **Function Signatures**: All test functions updated to match new language-aware signatures

### Testing
- **44 Tests Passing**: All tests now pass with 0 failures
- **Complete Coverage**: Full test coverage of all i18n-based functionality
- **Mock Validation**: Comprehensive mock validation for all external dependencies
- **Error Scenarios**: Complete testing of error scenarios with new i18n system
- **Production Readiness**: All tests validate production-ready i18n implementation

## [0.3.20] - 2025-01-21

### Added
- **Complete UI Localization**: All remaining user-facing flows now fully localized
  - /status command: All account status fields use i18n keys (EN/RU)
  - /profile command: All profile field names, values, and button labels localized
  - /daily command: All macro names, nutrition breakdown, and progress indicators localized
  - /help command: Complete help guide text uses i18n keys
  - All keyboard button labels use i18n for full localization

### Changed
- **Refactored Command Handlers for Language Support**
  - `status_callback()` now uses i18n for all output fields
  - `show_profile_menu()` and `show_profile_info()` use i18n for all field names and values
  - `show_daily_plan()` uses i18n for all macro names and nutrition breakdown
  - `help_callback()` uses i18n for all help text sections
  - All keyboard creation functions use i18n for button labels

### Fixed
- **Eliminated All Hardcoded English Text in UI**
  - No more English text in account status for Russian users
  - All profile field names and values properly localized
  - All macro names (Protein, Fats, Carbs) now use i18n keys
  - All button labels and navigation elements fully translated
  - Consistent language experience across all bot interactions

### Technical
- **Enhanced i18n System**
  - Added 30+ new translation keys for profile fields and values
  - Added 20+ new translation keys for macro names and nutrition terms
  - Added 15+ new translation keys for button labels and UI elements
  - Added 10+ new translation keys for activity levels and goals
  - All translations provided in both English and Russian
  - Complete coverage of all user-facing text elements

### User Experience
- **Fully Localized Interface**: Users now experience complete language consistency
- **Seamless Multilingual Support**: All commands and UI elements respect user's language preference
- **Professional Localization**: All text elements properly translated and formatted
- **Consistent Experience**: No more mixed language content in any bot interaction

## [0.3.19] - 2025-01-21

### Added
- **Complete i18n refactor for all dynamic content**
  - All daily recommendations now use i18n keys (both EN/RU)
  - All goal-specific advice fully localized
  - Weekly report messages fully i18n-based
  - Water tracker messages fully i18n-based
  - Nutrition insights headers and sections fully localized
  - All error messages properly localized

### Changed
- **Refactored functions for language support**
  - `get_daily_recommendations()` now accepts language parameter
  - `get_goal_specific_advice()` now accepts language parameter
  - `generate_nutrition_insights()` uses i18n for all headers
  - `weekly_report_callback()` and `weekly_report_command()` fully i18n-based
  - `water_tracker_callback()` and `water_tracker_command()` fully i18n-based

### Fixed
- **Eliminated all hardcoded English text**
  - No more English "leakage" in recommendations for Russian users
  - All dynamic advice and tips now respect user's language
  - All report headers and sections properly localized
  - Consistent language experience across all bot features

### Technical
- **Enhanced i18n system**
  - Added 50+ new translation keys for recommendations
  - Added 20+ new translation keys for advice and reports
  - Added 15+ new translation keys for water tracker
  - Added 10+ new translation keys for nutrition insights
  - All translations provided in both English and Russian

## [0.3.18] - 2025-01-21

### Added
- **Complete Multilingual Support**: All bot features now fully translated to English and Russian
- **Profile Setup Translations**: Complete translation of profile setup process (age, gender, height, weight, activity, goals)
- **Photo Analysis Translations**: All photo analysis messages, errors, and tips translated
- **Daily Plan Translations**: Complete translation of daily nutrition plan and progress tracking
- **Nutrition Insights Translations**: All nutrition analysis messages and recommendations translated
- **OpenAI Language-Aware Prompts**: ML service now uses Russian prompts for Russian users and English for others
- **Comprehensive Error Messages**: All error messages and rate limiting notifications translated
- **Language Detection Testing**: Comprehensive test suite for language detection and translation system

### Changed
- **Profile Setup Flow**: All profile setup steps now display in user's preferred language
- **Photo Analysis Experience**: Analysis results, tips, and error messages now in user's language
- **Daily Plan Interface**: Progress tracking, recommendations, and status messages translated
- **Nutrition Analysis**: All nutrition insights and recommendations display in user's language
- **ML Service Integration**: OpenAI prompts now adapt to user's language preference
- **Error Handling**: All system errors and user-facing messages now support both languages
- **User Experience**: Seamless multilingual experience across all bot features

### Fixed
- **Missing Translations**: Added translations for all previously hardcoded English text
- **Profile Validation Messages**: Age, height, weight validation errors now translated
- **Photo Analysis Errors**: "No food detected", "Analysis failed" messages translated
- **Daily Plan Status**: Progress status messages and recommendations translated
- **Nutrition Insights**: Profile completion prompts and error messages translated
- **Language Consistency**: All user interactions now consistently use detected language
- **OpenAI Response Language**: Analysis results now provided in user's preferred language

### Technical
- **I18n System Enhancement**: Extended translation system to cover all bot features
- **ML Service Updates**: Added user_language parameter to photo analysis API
- **Prompt Localization**: OpenAI prompts now support Russian and English languages
- **Translation Coverage**: 100% of user-facing messages now translated
- **Language Detection**: Comprehensive testing confirms accurate language detection
- **API Integration**: ML service properly receives and uses user language preference
- **Error Message System**: Centralized error message translation system

### Database
- **Language Storage**: User language preferences properly stored and retrieved
- **Country Detection**: Language detection based on country codes working correctly
- **Phone Number Detection**: Russian phone number patterns properly detected
- **Language Persistence**: Language changes properly saved and maintained

### Testing
- **Language Detection Tests**: 25 test cases covering all country and phone patterns
- **Translation Tests**: Complete translation system validation
- **Language Name Tests**: Proper language name display verification
- **Parameter Formatting**: Translation parameter substitution working correctly

## [0.3.17] - 2025-01-21

### Fixed
- **YooKassa/Telegram Payments**: Payments now work with auto-receipt (фискализация) enabled in YooKassa
- **Receipt Data**: Added provider_data with full receipt (items, tax_system_code, vat_code, etc.) to all Telegram invoices
- **Email Collection**: Enabled need_email and send_email_to_provider so Telegram collects user email for receipt delivery automatically
- **Amount Format**: Fixed amount formatting in provider_data (now always in RUB, not kopecks)
- **Production Payment Reliability**: Payments now pass all YooKassa and Telegram requirements for production

### Changed
- **Payment Plan Prices**: Set Basic Plan to 99 RUB, Pro Plan to 149 RUB for production
- **Detailed Logging**: Added logging of provider_token and all payment parameters for easier debugging

### Technical
- **provider_data**: Now always included in answer_invoice for Telegram/YooKassa payments
- **Email via Telegram**: No need to collect email in chat, Telegram form handles it
- **Compliant with YooKassa Docs**: Integration now matches YooKassa/Telegram fiscalization requirements

### Note
- Payments with auto-receipt (фискализация) now fully supported for Russian users
- If YooKassa settings change, only provider_data and price in config.py need to be updated

## [0.3.16] - 2025-01-21

### Added
- **Multilingual Support**: Complete Russian and English language support for the entire bot
- **Automatic Language Detection**: Smart language detection based on user's country and phone number
- **Language Switching**: User can manually switch between languages via /language command
- **Russian-Speaking Countries**: Automatic Russian language for Russia, Belarus, Kazakhstan, Kyrgyzstan, Armenia, Azerbaijan, Georgia, Uzbekistan
- **Phone Number Detection**: Russian language detection for +7 and 8 phone number patterns
- **Database Language Storage**: User language preferences stored in database with country and phone number
- **Comprehensive Translations**: All bot messages, buttons, and error messages translated to Russian
- **Language Menu**: Interactive language selection menu with flag emojis

### Changed
- **User Experience**: Bot now responds in user's preferred language automatically
- **Database Schema**: Added language, country, and phone_number columns to users table
- **Message System**: All hardcoded messages replaced with i18n translation system
- **Keyboard System**: All interactive keyboards now support multiple languages
- **Error Messages**: Rate limiting and error messages now display in user's language

### Fixed
- **Language Button Error**: Fixed "An error occurred" when clicking language button
- **I18n Parameter Conflict**: Resolved `get_text()` function parameter conflict with `language` argument
- **Translation Formatting**: Fixed translation parameter naming from `{language}` to `{lang_name}`
- **Language Menu Display**: Corrected language selection menu to show proper language names

### Technical
- **I18n System**: Created comprehensive internationalization system with i18n.py
- **Language Detection**: Implemented smart language detection algorithm
- **Database Migration**: Added multilingual support to database schema
- **Translation Management**: Centralized translation system with fallback to English
- **Language Handlers**: New language.py module for language switching functionality
- **Updated Handlers**: All command handlers updated to use i18n system
- **Keyboard Updates**: All keyboard functions updated to support language parameter
- **Parameter Naming**: Fixed translation parameter conflicts by using `lang_name` instead of `language`

### Database Changes
- Added `language` column (TEXT, default 'en', check for 'en' or 'ru')
- Added `country` column (TEXT) for language detection
- Added `phone_number` column (TEXT) for language detection
- Added index on language column for performance
- Updated user_activity_summary view to include language information

### Language Support
- **English (en)**: Default language for international users
- **Russian (ru)**: Primary language for Russian-speaking countries
- **Automatic Detection**: Based on Telegram language_code, country, and phone patterns
- **Manual Override**: Users can change language via /language command
- **Persistent Storage**: Language preference saved in database

## [0.3.15] - 2024-12-18

### Fixed
- **Telegram Payment Amount Error**: Fixed `CURRENCY_TOTAL_AMOUNT_INVALID` error by setting minimum accepted amounts
- **Payment Testing**: Updated test amounts to 10 RUB and 50 RUB (minimum Telegram-accepted amounts)
- **Invoice Creation**: Resolved issue preventing invoice creation in Telegram payments

### Changed
- **Basic Plan**: Updated from 1 RUB to 10 RUB (minimum Telegram amount)
- **Pro Plan**: Updated from 5 RUB to 50 RUB (minimum Telegram amount)
- **Payment Validation**: Ensured all amounts meet Telegram's minimum requirements

### Technical
- **Minimum Amounts**: Telegram requires minimum amounts for payment processing
- **Testing Ready**: Payment system now ready for real testing with acceptable amounts
- **Error Resolution**: Fixed `CURRENCY_TOTAL_AMOUNT_INVALID` error in production

### Note
Current pricing is set to minimum Telegram-accepted amounts for testing.
Will be reverted to normal pricing (99 RUB / 399 RUB) after testing completion.

## [0.3.14] - 2024-12-18

### Fixed
- **Code Deduplication**: Eliminated all duplicate payment configurations following DRY principles
- **Single Source of Truth**: Unified all payment configs into one centralized `PAYMENT_PLANS`
- **Clean Architecture**: Removed redundant `YOOKASSA_PAYMENT_PLANS` and `DISPLAY_PRICES` configurations

### Technical
- **Unified Config**: All services now use single `PAYMENT_PLANS` from main config
- **Dynamic Adaptation**: YooKassa and Stripe configs automatically adapt from main config
- **Eliminated Redundancy**: Removed duplicate payment amount definitions across codebase

## [0.3.13] - 2024-12-18

### Added
- **Single Payment Configuration**: Unified payment config system with single source of truth
- **Temporary Test Pricing**: Set payment amounts to 1 RUB and 5 RUB for production payment testing
- **Dynamic Configuration**: All payment services now use centralized `PAYMENT_PLANS` config

### Changed
- **Basic Plan**: Temporarily reduced from 99 RUB to 1 RUB for testing
- **Pro Plan**: Temporarily reduced from 399 RUB to 5 RUB for testing
- **Removed Code Duplication**: Eliminated duplicate payment configurations across services
- **Unified Config**: Single `PAYMENT_PLANS` in config.py replaces multiple separate configs

### Removed
- **Duplicate Configurations**: Removed `YOOKASSA_PAYMENT_PLANS` and `DISPLAY_PRICES` 
- **Unused Environment Variables**: Removed unused `YOOKASSA_PRICE_RUB`, `YOOKASSA_CREDITS`, `YOOKASSA_DESCRIPTION`
- **Hardcoded Values**: Removed all hardcoded payment amounts from handlers

### Technical
- **Single Source of Truth**: All payment amounts now controlled from one place in `config.py`
- **Automatic Adaptation**: YooKassa and Stripe configs automatically adapt from main config
- **Dynamic Pricing**: All UI elements calculate prices dynamically from config
- **Clean Architecture**: Eliminated code duplication following DRY principles

### Note
Current pricing is temporary for testing real payments in production environment. 
Will be reverted to normal pricing (99 RUB / 399 RUB) after testing completion.

## [0.3.12] - 2024-12-18

### Fixed
- **Critical User ID Bug**: Fixed nutrition insights callback using bot ID instead of user ID
- **Callback Handler**: Updated `nutrition_insights_callback` to use `callback.from_user.id` 
- **Production Logs**: Resolved user ID mismatch in production causing incorrect data association

### Technical
- Fixed `nutrition_insights_callback` implementation to directly use callback user ID
- Added comprehensive testing to verify user ID handling
- Prevented bot ID (7918860162) from being used instead of actual user ID

## [0.3.11] - 2024-12-18

### Fixed
- **Telegram Markdown Parsing**: Fixed critical "Can't find end of the entity starting at byte offset" error
- **Nutrition Insights Crash**: Implemented markdown sanitization to prevent malformed patterns
- **Bold Entity Handling**: Fixed cross-line bold entities and multiple asterisk patterns

### Added
- **Markdown Sanitization**: New `sanitize_markdown_text()` function in nutrition handler
- **Comprehensive Testing**: 7 test cases covering all markdown edge cases
- **GitHub Actions Fix**: Updated deprecated `upload-artifact@v3` to `v4`

### Technical
- Fixed `**\n**` patterns that caused cross-line bold entity errors
- Fixed triple/quadruple asterisk patterns (`***`, `****`)
- Updated all nutrition headers with proper colon formatting
- Added extensive test coverage for markdown sanitization

## [0.3.10] - 2024-12-18

### Added
- **Comprehensive Testing System**: Built 45+ unit and integration tests covering all critical components
- **Coverage System**: Implemented advanced coverage reporting with 85% minimum requirement
- **Deployment Protection**: Created pre-deployment testing script ensuring code quality
- **Testing Infrastructure**: Organized test structure with unit, integration, and coverage folders

### Fixed
- **Critical NoneType Error**: Fixed nutrition insights crash when user profile is None
- **Version Management**: Implemented centralized version system with dynamic imports
- **Profile Validation**: Added proper None checks for user profiles in nutrition insights

### Technical
- Created comprehensive test suite in `tests/` directory
- Added coverage reporting system with pytest-cov
- Implemented deployment protection requiring tests to pass
- Updated all version references to use dynamic VERSION variable
- Added proper error handling for None profile scenarios

## [0.3.9] - 2024-12-18

### Added
- **Motivational BMI Messaging**: Added encouraging messages for all BMI categories
- **Metabolic Age Motivation**: Enhanced metabolic age display with positive reinforcement
- **Nutrition Recommendations Rewrite**: Completely rewrote with supportive, motivational tone
- **Random Motivational Wins**: Added rotating positive messages for user encouragement
- **Enhanced Goal Advice**: Improved goal-specific advice with motivational language

### Fixed
- **Nutrition Insights Profile Bug**: Fixed validation to check specific profile fields instead of general existence
- **User Experience**: Improved overall tone and messaging throughout nutrition features

### Technical
- Enhanced profile validation in nutrition insights
- Added motivational message randomization system
- Improved error handling for profile-related operations

## [0.3.8] - 2024-12-17

### Fixed
- **Callback Query Bug**: Fixed critical issue where callback queries were processed as regular messages
- **User ID Extraction**: Proper user ID handling for different message types (Message vs CallbackQuery)
- **Nutrition Insights Access**: Fixed callback-based nutrition insights not working properly

### Added
- **Robust Message Handling**: Enhanced message processing to handle both regular messages and callback queries
- **User ID Validation**: Added proper user ID extraction logic for different Telegram message types
- **Error Logging**: Improved error logging for callback query processing

### Technical
- Fixed `nutrition_insights_command` to properly handle CallbackQuery objects
- Added type checking for Message vs CallbackQuery in user ID extraction
- Enhanced error handling for callback query processing

## [0.3.7] - 2024-12-17

### Added
- **Comprehensive Nutrition Insights**: Complete nutrition analysis with BMI, metabolic age, and personalized recommendations
- **User Profile System**: Detailed user profiles with health metrics, goals, and dietary preferences
- **BMI Calculation**: Automatic BMI calculation with health status indicators
- **Metabolic Age Analysis**: Advanced metabolic age calculation based on user metrics
- **Personalized Recommendations**: Tailored nutrition advice based on user goals and profile
- **Profile Management**: Create, update, and view user profiles with comprehensive health data

### Technical
- Added user profile creation and management system
- Implemented comprehensive nutrition analysis algorithms
- Created detailed user profile storage in Supabase
- Added BMI and metabolic age calculation functions
- Enhanced nutrition insights with personalized recommendations

## [0.3.6] - 2024-12-17

### Fixed
- **Photo Processing Bug**: Fixed critical issue where photo processing failed due to incorrect user ID handling
- **User ID Extraction**: Proper user ID extraction from Telegram messages during photo processing
- **Error Handling**: Enhanced error handling for photo processing failures

### Added
- **Robust Photo Processing**: Improved photo processing with better error handling
- **User ID Validation**: Added proper user ID extraction and validation for photo processing
- **Enhanced Logging**: Better logging for photo processing operations

### Technical
- Fixed user ID extraction in photo processing handler
- Added comprehensive error handling for photo processing
- Enhanced logging for debugging photo processing issues

## [0.3.5] - 2024-12-17

### Fixed
- **OpenAI Connection Error**: Fixed connection issues with OpenAI API
- **Model Configuration**: Corrected OpenAI model configuration and API calls
- **Photo Analysis**: Restored photo analysis functionality with proper OpenAI integration

### Added
- **Enhanced Error Handling**: Better error handling for OpenAI API failures
- **Model Optimization**: Optimized OpenAI model usage for better performance
- **Connection Resilience**: Improved connection handling for external API calls

### Technical
- Updated OpenAI API integration
- Fixed model configuration issues
- Enhanced error handling for API calls

## [0.3.4] - 2024-12-17

### Fixed
- **Critical Import Error**: Fixed missing `get_user_total_paid` function import in commands.py
- **Function Dependencies**: Resolved import dependencies for user payment calculations
- **Status Command**: Fixed `/status` command functionality with proper imports

### Added
- **Payment Tracking**: Enhanced payment tracking functionality
- **User Status**: Improved user status reporting with payment information
- **Import Validation**: Added proper import validation for all required functions

### Technical
- Fixed import statements in commands.py
- Added missing function imports for payment tracking
- Enhanced error handling for payment-related operations

## [0.3.3] - 2024-12-17

### Fixed
- **Bot Initialization**: Fixed critical bot initialization error
- **Command Registration**: Resolved command handler registration issues
- **Application Startup**: Fixed application startup sequence

### Added
- **Startup Validation**: Enhanced startup validation and error handling
- **Command System**: Improved command registration and handling
- **Error Recovery**: Better error recovery during bot initialization

### Technical
- Fixed bot initialization sequence
- Enhanced command handler registration
- Improved error handling during startup

## [0.3.2] - 2024-12-17

### Fixed
- **Environment Variables**: Fixed missing environment variable handling
- **Configuration Loading**: Resolved configuration loading issues
- **Service Integration**: Fixed integration between services

### Added
- **Environment Validation**: Enhanced environment variable validation
- **Configuration Management**: Improved configuration management system
- **Service Health Checks**: Added health checks for service integration

### Technical
- Enhanced environment variable handling
- Improved configuration loading
- Added service integration validation

## [0.3.1] - 2024-12-17

### Fixed
- **Database Connection**: Fixed Supabase connection issues
- **User Management**: Resolved user creation and management problems
- **Credit System**: Fixed credit tracking and management

### Added
- **Database Health Checks**: Added database connection health checks
- **User System**: Enhanced user management system
- **Credit Tracking**: Improved credit tracking and allocation

### Technical
- Fixed Supabase integration
- Enhanced user management functions
- Improved credit system reliability

## [0.3.0] - 2024-12-17

### Added
- **Advanced Nutrition Analysis**: Complete nutrition analysis with detailed KBZHU breakdown
- **Credit System**: Implemented credit-based usage system with payment integration
- **User Management**: Comprehensive user management with Supabase integration
- **Payment Processing**: Integrated YooKassa and Stripe payment systems
- **Telegram Bot**: Full-featured Telegram bot with photo analysis capabilities
- **Admin Panel**: Admin bot for monitoring and management
- **ML Integration**: Advanced machine learning for food recognition and analysis

### Technical
- Complete rewrite of the application architecture
- Microservices architecture with multiple specialized services
- Advanced error handling and logging
- Comprehensive testing system
- Production-ready deployment configuration

### Infrastructure
- Docker containerization for all services
- Nginx reverse proxy configuration
- SSL/TLS security implementation
- Environment-based configuration management
- Health monitoring and alerting system

## [0.2.0] - 2024-12-16

### Added
- **Photo Processing**: Basic photo analysis functionality
- **User System**: Initial user management system
- **Database Integration**: Basic database operations
- **API Structure**: RESTful API foundation

### Technical
- Initial application structure
- Basic error handling
- Database schema design
- API endpoint definitions

## [0.1.0] - 2024-12-15

### Added
- **Project Initialization**: Initial project setup and structure
- **Basic Framework**: Core application framework
- **Development Environment**: Development environment setup
- **Documentation**: Initial documentation structure

### Technical
- Project structure definition
- Initial dependencies
- Basic configuration system
- Development workflow setup
