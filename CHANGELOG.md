# Changelog

## [0.3.5] - 2024-01-XX

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

### 🛠️ **Improvements**
- **User Experience**: All text now in English for consistency
- **Error Handling**: Credits are not deducted when analysis fails
- **Security**: Rate limiting prevents system abuse
- **Validation**: Comprehensive input validation for all profile fields
  - Age: 10-120 years
  - Height: 100-250 cm
  - Weight: 30-300 kg
- **Testing**: Created comprehensive local testing guide

### 🔧 **Technical Changes**
- Added `RateLimiter` class for anti-spam protection
- Implemented middleware for rate limiting
- Enhanced photo handler with size checks
- Improved FSM state management
- Better error messages and user feedback

### 📋 **Testing**
- Created `TESTING_GUIDE.md` with comprehensive testing strategy
- Added `test_db_connection.py` for database connection testing
- Defined test phases from basic commands to performance testing
- Mock ML service setup for local testing

### 🐛 **Bug Fixes**
- Fixed profile setup interruption handling
- Fixed credits deduction on failed analysis
- Fixed text language consistency (all English)
- Fixed FSM state management issues

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
