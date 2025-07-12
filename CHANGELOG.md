# Changelog

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

### 📋 **Files Modified**
- `handlers/keyboards.py` - New shared keyboard utilities module
- `handlers/commands.py` - Removed duplicate keyboard functions, import from keyboards
- `handlers/payments.py` - Import keyboard utilities from keyboards module
- `handlers/daily.py` - Import keyboard utilities from keyboards module
- `handlers/photo.py` - Import keyboard utilities from keyboards module
- `handlers/profile.py` - Enhanced error handling for calorie calculation
- `common/supabase_client.py` - Improved calculate_daily_calories function with validation

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
