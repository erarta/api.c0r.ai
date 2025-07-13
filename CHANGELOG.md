# Changelog

## [v0.3.11] - 2025-01-13

### Fixed
- 🔥 **CRITICAL**: Fixed Telegram markdown parsing error in nutrition insights that was causing crashes
- 📝 Added comprehensive markdown sanitization function to prevent `**\n**` patterns and other problematic Telegram entities
- 🔧 Fixed malformed markdown headers that were causing "Can't find end of entity" errors
- 📊 Improved nutrition insights text formatting for better Telegram compatibility
- 🚀 Fixed deprecated `upload-artifact@v3` to `@v4` in GitHub Actions workflow
- 🧪 Fixed CI test failures by creating dependency-free tests for critical functionality

### Added
- 🧪 Created comprehensive test suite for markdown sanitization with 7 test cases
- 🔍 Added byte position analysis tests to understand parsing issues
- 📝 Implemented text sanitization function that fixes:
  - `**\n**` patterns (bold across newlines)
  - `***` patterns (triple asterisks)
  - `****` patterns (quadruple asterisks)
  - `**  **` patterns (empty bold entities)
- 📋 Created mandatory testing requirements rule in `.cursor/rules/testing_requirements.md`
- 🐳 Added comprehensive local Docker testing script with health checks and troubleshooting
- 📚 Created complete Docker testing guide with best practices and troubleshooting
- 🧪 Created dependency-free critical tests for CI environment (`test_nutrition_sanitization_simple.py`)

### Technical
- 🛠️ Added `sanitize_markdown_text()` function to nutrition handler
- 📋 Updated all section headers to use proper colon formatting
- 🔄 Implemented automatic text sanitization in `generate_nutrition_insights()`
- 📊 Enhanced markdown validation functions for better testing
- 🧪 Established mandatory testing workflow: unit tests + integration tests + coverage ≥85%
- 🔧 Improved CI/CD pipeline reliability with updated GitHub Actions

### Development Infrastructure
- 📝 Enforced test-first development approach for all new features
- 🛡️ Enhanced deployment protection with comprehensive test suite
- 🐳 Standardized local Docker testing procedures
- 📋 Created templates and guidelines for consistent test structure

## [v0.3.10] - 2025-01-12

### 🐛 **Critical Bug Fixes**
- **Fixed Nutrition Insights NoneType Error**: Resolved crash when users without profiles tried to access nutrition insights
  - **Error**: `'NoneType' object has no attribute 'get'` when profile is None
  - **Fix**: Added proper None check before calling profile.get() method
  - **Impact**: Users can now safely access nutrition insights feature and get clear profile setup guidance

- **Fixed Callback User ID Confusion**: Resolved critical issue where callbacks used wrong user ID
  - **Error**: Nutrition insights and water tracker were getting bot ID (7918860162) instead of actual user ID (391490)
  - **Root Cause**: Callback functions used `callback.message.from_user.id` (bot's message) instead of `callback.from_user.id` (user who clicked)
  - **Fix**: Created proper callback handlers that extract user ID from callback query correctly
  - **Impact**: All callback-based features now work correctly for the actual user who clicked the button

### 🔧 **Technical Improvements**
- **Dynamic Version Management**: Implemented centralized version system
  - **New**: Created `config.py` with VERSION variable for centralized version management
  - **Updated**: All system version references now use dynamic VERSION variable
  - **Benefit**: Version updates now only require changing one variable, eliminating version inconsistencies

### 🚀 **Deployment & Testing Enhancements**
- **Mandatory Testing in Deployment**: Added comprehensive testing steps to deployment process
  - **New**: Created full-featured `scripts/deploy.sh` with mandatory test execution
  - **Updated**: GitHub Actions workflow now includes testing job before deployment
  - **Protection**: Deployment is blocked if any tests fail
  - **Impact**: Prevents broken code from reaching production

- **Integration Tests Organization**: Moved and organized integration tests
  - **Moved**: All integration tests from root to `tests/integration/` directory
  - **New**: Created `tests/run_integration_tests.py` runner for external service tests
  - **Updated**: Main test runner now includes external integration tests
  - **Impact**: Better organized test structure and comprehensive coverage
  - **Current Version**: Automatically displays v0.3.10 across all system messages

### 🧪 **Comprehensive Testing System**
- **Test Suite Creation**: Built comprehensive testing infrastructure to prevent future production bugs
  - **Unit Tests**: 45+ tests covering all critical components (nutrition, commands, calculations)
  - **Integration Tests**: Full user journey and critical path testing
  - **Coverage Requirement**: Minimum 85% code coverage enforced
  - **Deployment Protection**: Tests must pass before any production deployment

- **Test Structure**: Organized testing framework in `tests/` directory
  - `tests/unit/` - Component-specific unit tests
  - `tests/integration/` - End-to-end integration tests
  - `tests/coverage/` - Coverage reports and analysis
  - `tests/deploy_test.sh` - Pre-deployment validation script

- **Coverage Analysis**: Advanced coverage reporting and monitoring
  - **HTML Reports**: Interactive coverage visualization
  - **JSON Reports**: Machine-readable coverage data
  - **Markdown Reports**: Human-readable coverage summaries
  - **Critical Component Focus**: 85%+ coverage required for core handlers

- **Deployment Integration**: Seamless integration with deployment pipeline
  - **Pre-deployment Tests**: Mandatory test execution before production
  - **Syntax Validation**: Python syntax checking for all critical files
  - **Import Verification**: Ensures all imports work correctly
  - **Version Consistency**: Validates version display across components

### 📋 **Code Quality & Maintenance**
- **Better Error Handling**: Enhanced profile validation in nutrition insights
- **Centralized Configuration**: Improved maintainability with config.py
- **Automated Bug Detection**: Tests specifically target the original nutrition insights bug
- **Continuous Quality Assurance**: Ongoing protection against regression bugs

### 🛡️ **Production Safety**
- **Deployment Protection**: Tests act as safety net preventing broken code deployment
- **Critical Path Coverage**: Tests cover exact scenarios that caused original bug
- **Regression Prevention**: Comprehensive test suite prevents similar bugs in future
- **Quality Gates**: 85% coverage requirement ensures thorough testing

---

## [0.3.9] - 2025-01-20

### 💪 **Motivational UX Enhancements**
- **Fixed Nutrition Insights Bug**: Now properly checks specific profile fields instead of relying on has_profile flag
  - Better error messaging showing exactly which fields are missing
  - More accurate profile completeness detection

- **Motivational BMI Messaging**: Transformed clinical BMI categories into supportive, encouraging messages
  - Underweight: "Let's focus on healthy weight gain together! 🌱 Every nutritious meal is a step forward!"
  - Normal: "Fantastic! You're in the ideal range! 🎉 Keep up the great work maintaining your health!"
  - Overweight: "You're taking the right steps by tracking! 💪 Small changes lead to big results!"
  - Obese: "Every healthy choice counts! 🌟 You're already on the path to positive change!"

- **Enhanced Metabolic Age Encouragement**: Added motivational context to metabolic age analysis
  - Younger metabolic age: "Amazing! Your healthy lifestyle is paying off! Keep doing what you're doing! 🚀"
  - Older metabolic age: "No worries! With consistent nutrition and activity, you can improve this! 💪"
  - Normal metabolic age: "Perfect balance! You're maintaining great metabolic health! 🎯"

- **Supportive Nutrition Recommendations**: Completely rewritten recommendations with positive, encouraging tone
  - Replaced clinical language with supportive, action-oriented advice
  - Added context and reasoning behind recommendations
  - Included encouragement for all activity levels and goals

- **Random Motivational "Wins"**: Added rotating positive reinforcement messages
  - "🌟 You're taking control of your health by tracking nutrition!"
  - "🎉 Every food analysis brings you closer to your goals!"
  - "💪 Small consistent steps lead to amazing transformations!"
  - "🚀 You're investing in the most important asset - your health!"
  - "✨ Progress, not perfection - you're doing great!"

- **Goal-Specific Motivational Advice**: Enhanced goal-specific guidance with encouraging language
  - Weight loss: Emphasized "gentle deficit" and "sustainable wins"
  - Weight gain: Focused on "healthy weight building" and "steady progress"
  - Maintenance: Celebrated "sweet spot" achievement and "joyful eating"

### 🔧 **Technical Improvements**
- **Better Profile Validation**: More granular checking of required fields for nutrition insights
- **Enhanced Data Structure**: Added motivation fields to BMI and metabolic age calculations
- **Improved Error Messaging**: Specific feedback on missing profile fields

---

## [0.3.8] - 2025-01-20

### 🔬 **New Advanced Nutrition Features**
- **Nutrition Insights**: Comprehensive nutrition analysis with BMI, metabolic age, and recommendations
  - BMI calculation with category classification (underweight, normal, overweight, obese)
  - Ideal weight range using multiple formulas (BMI-based and Broca)
  - Metabolic age estimation based on BMR and lifestyle factors
  - Personalized macro distribution (protein, carbs, fats) based on goals
  - Meal portion breakdown for optimal calorie distribution
  - Goal-specific advice for weight loss, gain, or maintenance
  - Command: `/insights` or 🔬 Nutrition Insights button

- **Water Tracker**: Personalized hydration recommendations
  - Calculate daily water needs based on weight and activity level
  - Activity-based water bonus calculations
  - Practical tips for staying hydrated
  - Command: `/water` or 💧 Water Tracker button

- **Weekly Report**: Nutrition progress tracking (foundation)
  - Weekly meal analysis framework
  - Consistency scoring system
  - Trend analysis for goal progress
  - Command: `/report` or 📈 Weekly Report button

### 🧮 **Advanced Calculation Engine**
- **New Nutrition Calculations Module**: `common/nutrition_calculations.py`
  - BMI with detailed categorization and health indicators
  - Ideal weight using BMI-based (20-25) and Broca formulas
  - Water needs: 35ml/kg base + activity multipliers (1.0-1.8x)
  - Metabolic age estimation using BMR, BMI, and activity factors
  - Macro distribution optimization based on goals:
    - Weight loss: 30% protein, 25% fat, 45% carbs
    - Weight gain: 25% protein, 25% fat, 50% carbs
    - Maintenance: 25% protein, 30% fat, 45% carbs
  - Meal portion timing: breakfast 25%, lunch 40%, dinner 35%
  - Personalized nutrition recommendations engine

### 🎨 **Enhanced User Experience**
- **Expanded Main Menu**: Added 4 new nutrition features
  - Reorganized menu with better categorization
  - More comprehensive feature access
  - Clearer navigation flow
- **Smart Recommendations**: Context-aware nutrition advice
  - BMI-based food recommendations
  - Activity-level specific protein guidance
  - Goal-oriented meal timing advice
  - Hydration reminders based on weight and activity

---

## [0.3.7] - 2025-01-20

### 🚨 **Critical Bug Fix**
- **Circular Import Fix**: Resolved deployment-blocking circular import issue
  - **Issue**: `handlers/commands.py` ↔ `handlers/payments.py` circular import preventing API service startup
  - **Solution**: Created new `handlers/keyboards.py` module for shared keyboard utilities
  - **Impact**: API service now starts successfully, deployment restored
  - **Files affected**: All handler files now import from centralized keyboards module
  - **Error resolved**: `ImportError: cannot import name 'create_main_menu_keyboard' from partially initialized module`

### 🛠️ **Code Quality Improvements**
- **Enhanced Function Validation**: Improved `calculate_daily_calories()` function
  - Added comprehensive input validation with descriptive error messages
  - Implemented case-insensitive input handling (`.lower()` normalization)
  - Enhanced error handling with try-catch blocks in all calling functions
  - Switched from `int()` to `round()` for more accurate calorie calculations
  - Added proper `ValueError` exceptions for invalid inputs (gender, activity, goal)
  - Better user feedback when profile calculation fails

### 🔧 **Technical Improvements**
- **Modular Architecture**: Separated shared utilities to prevent circular imports
- **Better Error Handling**: Graceful handling of calculation errors in profile system
- **Code Organization**: Improved separation of concerns across handler modules
- **Production Stability**: Fixed critical deployment blocker affecting system availability

### 🎨 **UX Improvements**
- **Support Contact Updated**: Changed from @your_support_bot to team@c0r.ai
- **View Daily Plan Fixed**: Added missing `daily_callback` handler for button functionality
- **Enhanced Recommendations**: Dramatically improved daily nutrition recommendations
  - Added 50+ varied, personalized tips based on progress and goals
  - Implemented randomization for engaging, non-repetitive advice
  - Added motivational and educational bonus tips (30% chance)
  - Better categorization: morning, progress, meal suggestions, snacks
  - Enhanced tracking encouragement and goal-specific feedback

### 🖼️ **Assets & Visuals**
- **Invoice Logo Fixed**: Updated photo_url to use @logo_v2.png
- **Assets Serving Restored**: Re-enabled static file serving for logos
  - Fixed Dockerfile to properly copy assets from root directory
  - Assets now available at https://api.c0r.ai/assets/logo_v2.png

### 📋 **Files Modified**
- `handlers/keyboards.py` - New shared keyboard utilities module
- `handlers/commands.py` - Removed duplicate keyboard functions, import from keyboards, support contact fix
- `handlers/payments.py` - Import keyboard utilities from keyboards module, logo_v2.png fix
- `handlers/daily.py` - Import keyboard utilities from keyboards module, enhanced recommendations, daily_callback
- `handlers/photo.py` - Import keyboard utilities from keyboards module
- `handlers/profile.py` - Enhanced error handling for calorie calculation
- `common/supabase_client.py` - Improved calculate_daily_calories function with validation
- `api.c0r.ai/app/main.py` - Re-enabled assets serving
- `api.c0r.ai/Dockerfile` - Fixed assets copying from root directory

---

## [0.3.6] - 2025-01-20

### 🚀 **New Features**
- **Enhanced UX Navigation**: Added Main Menu button to all messages without reply buttons
  - Users can now always return to main menu from any message
  - No more "dead-end" messages where users don't know what to do next
  - Consistent navigation throughout the bot experience
- **R2 Diagnostics**: Added debugging endpoints for Cloudflare R2 storage
  - `/debug/r2` - Check R2 configuration and connection status
  - `/debug/recent-logs` - View recent photo analysis logs
  - Better visibility into photo storage issues

### 🛠️ **Improvements**
- **User Experience**: Significantly improved navigation and user guidance
  - Main Menu button added to: help messages, status messages, error messages, photo analysis failures
  - Users always have a clear path to return to main functionality
  - Better user retention and reduced confusion
- **Error Handling**: Enhanced error messages with navigation options
  - Payment errors now include Main Menu button
  - Photo analysis failures include Main Menu button
  - System errors provide way back to main functionality

### 🔧 **Technical Changes**
- Added `create_main_menu_keyboard()` utility function for consistent navigation
- Added `action_main_menu` handler for Main Menu button clicks
- Enhanced logging in R2 upload process for better debugging
- Added static file serving preparation (temporarily disabled)

### 🐛 **Bug Fixes**
- **Critical R2 Upload Fix**: Resolved BytesIO conversion error in photo uploads
  - Fixed `object of type '_io.BytesIO' has no len()` error
  - Added `.getvalue()` conversion from BytesIO to bytes
  - Photos now upload successfully to Cloudflare R2 storage
- **Docker Build Fix**: Resolved asset folder copying issues
  - Temporarily disabled assets mounting to prevent container crashes
  - Fixed Dockerfile build errors with non-existent assets folder
  - Improved container startup reliability
- **Invoice Photo URL**: Improved payment invoice appearance
  - Fixed photo URL in payment invoices
  - Better visual presentation during checkout process

### 🔍 **Production Improvements**
- **Enhanced Monitoring**: Better R2 upload logging and error tracking
- **Debugging Tools**: Added diagnostic endpoints for production troubleshooting
- **Container Stability**: Fixed Docker build and startup issues
- **Error Visibility**: Improved logging for R2 operations and photo processing

### 📋 **Technical Debt Resolution**
- Fixed BytesIO handling in multiple file download operations
- Improved error handling consistency across all handlers
- Better separation of concerns in navigation utilities
- Enhanced production debugging capabilities

---

## [0.3.5] - 2024-01-15

### 🚀 **New Features**
- **Anti-DDOS Protection**: Added rate limiting to prevent spam attacks
  - Photo analysis: Maximum 5 photos per minute per user
  - General commands: Maximum 20 commands per minute per user
  - Informative rate limit messages with countdown timers
- **Enhanced Photo Processing**: Improved error handling for photo analysis
  - Photo size limit: 10MB maximum
  - Better "no food detected" handling (credits not deducted)
  - Proper error messages for failed analysis
- **Profile System Improvements**: Fixed profile setup flow
  - Profile setup can be restarted anytime with `/profile` command
  - FSM state is cleared on profile command to prevent stuck states
  - Better user guidance during profile setup
- **Streamlined Profile Setup**: Removed intermediate steps for better UX
  - `/profile` command now starts setup immediately for new users
  - No more intermediate "Profile Setup" messages with buttons
  - Direct flow from command to first setup step
- **Enhanced UI/UX**: Replaced command mentions with interactive buttons
  - Profile setup messages now show "🚀 Set Up Profile" button instead of `/profile` command
  - Existing profile view shows "✏️ Edit Profile" button for editing
  - "Skip for now" option includes "👤 Set Up Profile" button for quick access
  - More intuitive and user-friendly interface throughout
- **Production Testing Tools**: Complete testing and monitoring infrastructure
  - Real-time monitoring script with color-coded logs
  - Automated connection tests for bot and database
  - Comprehensive testing guides and checklists

### 🛠️ **Improvements**
- **User Experience**: All text now in English for consistency
- **Profile Flow**: Eliminated unnecessary intermediate steps in profile setup
- **Button Interface**: Consistent use of interactive buttons instead of command references
- **Error Handling**: Credits are not deducted when analysis fails
- **Security**: Rate limiting prevents system abuse
- **Validation**: Comprehensive input validation for all profile fields
  - Age: 10-120 years
  - Height: 100-250 cm
  - Weight: 30-300 kg
- **Testing**: Created comprehensive local and production testing guides
- **Monitoring**: Real-time error monitoring and performance tracking

### 🔧 **Technical Changes**
- Added `RateLimiter` class for anti-spam protection
- Implemented middleware for rate limiting
- Enhanced photo handler with size checks
- Improved FSM state management
- Better error messages and user feedback
- Created production monitoring and testing infrastructure

### 📋 **New Files Added**
- `monitor_bot.sh` - Real-time monitoring script with color-coded output
- `test_bot_connection.py` - Telegram bot connection testing
- `test_db_connection.py` - Database connection testing  
- `PRODUCTION_TESTING_COMMANDS.md` - Detailed production testing guide
- `QUICK_PROD_TEST.md` - Quick 10-minute testing checklist
- `PRODUCTION_README.md` - Complete production deployment guide
- `TESTING_GUIDE.md` - Local development testing strategy

### 🐛 **Bug Fixes**
- Fixed profile setup interruption handling
- Fixed credits deduction on failed analysis
- Fixed text language consistency (all English)
- Fixed FSM state management issues

### 🎯 **Production Ready**
- Complete testing infrastructure for production deployment
- Real-time monitoring and error tracking
- Step-by-step testing scenarios
- Emergency response procedures
- Performance monitoring tools

---

## [0.3.4] - 2024-01-XX

### 🚀 **New Features**
- **Daily Nutrition Tracking**: Added `/daily` command to show daily calorie consumption and progress
- **Profile Management**: Added `/profile` command for user profile setup and management
- **Interactive User Interface**: Enhanced `/start` command with interactive buttons
- **Personal Data Collection**: Users can now input age, gender, height, weight, activity level, and goals
- **Daily Calorie Calculation**: Automatic TDEE calculation based on user profile

### 🛠️ **Improvements**
- **Enhanced Photo Analysis**: Now shows personalized progress for users with profiles
- **Better User Onboarding**: Interactive welcome message with action buttons
- **Comprehensive Help System**: Updated help command with all available features
- **Progress Tracking**: Visual progress bars and detailed daily statistics

### 🔧 **Technical Changes**
- Added FSM (Finite State Machine) for profile setup workflow
- Enhanced database schema with profile and detailed logging
- Improved logging system with structured action tracking
- Better error handling and user feedback

### 📋 **Database Schema Updates**
- Extended `users` table with personal data fields
- Enhanced `logs` table with action types and metadata
- Added proper nullable fields for flexible data storage

---

## [0.3.3] - 2024-01-XX

### 🚀 **New Features**
- **Enhanced Logging System**: Comprehensive user action logging with metadata
- **Cloudflare R2 Integration**: Photo storage in Cloudflare R2 with automatic URL generation
- **Improved Database Schema**: Enhanced users and logs tables with additional fields
- **Better Error Handling**: More informative error messages and proper exception handling

### 🛠️ **Improvements**
- **User Experience**: Better feedback messages and status updates
- **Database Operations**: Optimized queries and improved data structure
- **Photo Processing**: Enhanced photo handling with R2 storage integration
- **Code Organization**: Better separation of concerns and modular design

### 🔧 **Technical Changes**
- Added comprehensive logging function `log_user_action()`
- Enhanced database schema with nullable fields and metadata support
- Improved photo upload workflow with R2 integration
- Better error handling across all handlers

### 📋 **Documentation**
- Updated environment setup instructions
- Enhanced API documentation
- Better code comments and documentation strings

---

## [0.3.2] - 2024-01-XX

### 🚀 **New Features**
- **Credits System**: Users start with 3 free credits, 1 credit per photo analysis
- **Payment Integration**: `/buy` command with payment plans (Basic: 99 RUB, Pro: 399 RUB)
- **User Status**: `/status` command showing credits, total paid, and account info
- **Enhanced Photo Analysis**: Better food detection and KBZHU calculation

### 🛠️ **Improvements**
- **User Interface**: Interactive buttons and better message formatting
- **Database Operations**: Improved user management and credit tracking
- **Error Handling**: Better error messages and fallback scenarios
- **Performance**: Optimized database queries and response times

### 🔧 **Technical Changes**
- Added credit management system
- Enhanced database schema for user tracking
- Improved photo processing pipeline
- Better integration with ML service

---

## [0.3.1] - 2024-01-XX

### 🚀 **New Features**
- **Multi-service Architecture**: Separated ML, API, and Payment services
- **Docker Support**: Complete containerization with docker-compose
- **Enhanced Bot Commands**: `/start`, `/help`, `/status`, `/buy` commands
- **Payment Processing**: Integrated YooKassa and Stripe payment systems

### 🛠️ **Improvements**
- **Code Organization**: Better project structure with separated concerns
- **Documentation**: Comprehensive setup and deployment guides
- **Error Handling**: Improved error messages and user feedback
- **Performance**: Optimized service communication and response times

### 🔧 **Technical Changes**
- Implemented microservices architecture
- Added proper environment configuration
- Enhanced database schema
- Better API route management

---

## [0.3.0] - 2024-01-XX

### 🚀 **Initial Release**
- **Core Bot Functionality**: Basic Telegram bot with photo analysis
- **Food Recognition**: AI-powered food detection and calorie calculation
- **Database Integration**: Supabase for user and data management
- **ML Service**: OpenAI Vision API for food analysis
- **Basic Commands**: Essential bot commands for user interaction

### 🛠️ **Core Features**
- Photo-based food analysis
- KBZHU (Calories, Proteins, Fats, Carbohydrates) calculation
- User management and tracking
- Basic error handling and logging

### 🔧 **Technical Foundation**
- Python-based Telegram bot
- Supabase database integration
- OpenAI API integration
- Basic project structure

---

**Legend:**
- 🚀 New Features
- 🛠️ Improvements
- 🔧 Technical Changes
- 🐛 Bug Fixes
- 📋 Documentation/Testing
