# Changelog

All notable changes to this project will be documented in this file.

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
- **Version Update**: Updated to version 0.4.2

### Technical
- **I18n System**: Created comprehensive internationalization system with i18n.py
- **Language Detection**: Implemented smart language detection algorithm
- **Database Migration**: Added multilingual support to database schema
- **Translation Management**: Centralized translation system with fallback to English
- **Language Handlers**: New language.py module for language switching functionality
- **Updated Handlers**: All command handlers updated to use i18n system
- **Keyboard Updates**: All keyboard functions updated to support language parameter

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
