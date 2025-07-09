# Changelog

## [0.3.8] - 2024-07-09
### Added
- **YooKassa Integration Testing Suite**:
  - Comprehensive test scripts for YooKassa API integration
  - Telegram payments functionality testing (`test_telegram_payments.py`)
  - YooKassa API connection testing (`test_payment_simple.py`)
  - Provider token validation and format checking
  - Payment plans configuration testing
- **Production Deployment Preparation**:
  - Complete testing framework for payment integration
  - Bot testing script (`run_bot_test.py`) for payment flow validation
  - Production testing guide (`PAYMENT_TESTING_GUIDE.md`)
  - YooKassa API keys setup guide (`get_yookassa_keys.md`)
- **Enhanced Testing Infrastructure**:
  - Virtual environment setup for testing dependencies
  - Automated test execution with comprehensive reporting
  - Test cards and payment scenarios documentation
  - Webhook testing and validation tools

### Changed
- **Updated environment configuration** with proper YooKassa credentials structure
- **Enhanced payment testing** with real API integration tests
- **Improved documentation** for production deployment and testing
- **Standardized testing approach** across all payment components

### Fixed
- YooKassa API connection testing and error handling
- Provider token format validation
- Payment flow testing with proper error reporting
- Environment variable validation for production deployment

### Testing Results
- ✅ Telegram Bot API: Working (@c0rAIBot)
- ✅ Provider Token: Configured (381764678:TEST:130406)
- ✅ Telegram Payments: Ready for testing
- ✅ Payment Buttons: Configured and functional
- ✅ Invoice Creation: Successfully tested
- ⚠️ YooKassa API: Requires correct credentials from dashboard

### Documentation
- Added comprehensive production testing guide
- Step-by-step YooKassa API keys setup instructions
- Complete payment testing workflow documentation
- Troubleshooting guide for common deployment issues

## [0.3.7] - 2024-07-09
### Added
- **Telegram Native Payments Integration**:
  - Complete Telegram Payments support via BotFather and YooKassa
  - In-app payment experience without leaving Telegram
  - Native Telegram invoice messages with payment buttons
  - Pre-checkout validation for payment security
  - Automatic credit addition after successful payment
  - Payment plans: Basic (20 credits/99 RUB) and Pro (100 credits/399 RUB)
- **Enhanced bot commands**:
  - New `/buy` command for purchasing credits
  - Inline keyboard buttons for payment plan selection
  - Improved user experience with native Telegram UI
- **Payment handlers**:
  - `pre_checkout_query` handler for payment validation
  - `successful_payment` handler for credit addition
  - Callback query handler for payment button interactions

### Changed
- **Replaced external payment links** with native Telegram invoices
- **Updated photo handler** to show inline payment buttons instead of external URLs
- **Improved payment flow** - users never leave Telegram app
- **Enhanced user experience** with familiar Telegram payment interface
- **Updated environment configuration** with `YOOKASSA_PROVIDER_TOKEN` for Telegram payments

### Fixed
- Payment flow now works entirely within Telegram app
- Better error handling for payment failures
- Improved payment validation and security

### Documentation
- Added comprehensive `TELEGRAM_PAYMENTS_SETUP.md` guide
- Step-by-step BotFather configuration instructions
- YooKassa integration guide for Telegram payments
- Troubleshooting section for common issues

## [0.3.6] - 2024-07-09
### Added
- **Complete YooKassa payment integration**:
  - Real YooKassa SDK integration with proper API calls
  - Dynamic payment link generation via payment service
  - Webhook handler for processing successful payments
  - Automatic credit addition after successful payment
  - Payment success page with user-friendly design
  - Payment plans: Basic (20 credits/99 RUB) and Pro (100 credits/399 RUB monthly)
- **Enhanced payment service**:
  - Real invoice creation with YooKassa API
  - Proper error handling and logging
  - Integration with API service for credit management
  - HTML template support for payment success page

### Changed
- **Updated photo handler** to use real payment service instead of placeholder URLs
- **Improved environment configuration** with proper service URL management
- **Enhanced payment flow** with proper user experience from bot to payment to credit addition
- **Removed outdated environment variables** (YOOKASSA_PROVIDER_TOKEN) and updated examples

### Fixed
- Payment link generation now creates real YooKassa payment URLs
- Credit addition after payment now works through proper webhook handling
- Service communication between API and payment services

## [0.3.5] - 2024-07-09
### Added
- New `/status` command for Telegram bot:
  - Shows user account information (ID, credits, total paid, member since)
  - Displays system status and version information
  - Enhanced user experience with detailed account overview
- Updated `/help` command with improved formatting and command list
- Added proper datetime formatting for user creation dates

### Changed
- Enhanced help text with structured command list
- Improved user interaction with more informative status display

## [0.3.4] - 2024-07-08
### Added
- Production environment configuration for AWS deployment:
  - Created `.env.production.example` with AWS subdomain URLs
  - Added automatic environment switching script (`scripts/switch-env.sh`)
  - Enhanced deployment documentation with production URL configuration
- Production-ready Nginx configuration (`nginx.conf.production`):
  - Complete SSL setup for all three subdomains (api/ml/pay.c0r.ai)
  - Rate limiting per service with appropriate burst limits
  - Upstream servers configuration with keepalive
  - Security headers and proper proxy settings
  - Webhook endpoint handling with custom timeouts
- Automated production setup script (`scripts/setup-production.sh`):
  - Installs all required dependencies (Docker, Nginx, Certbot)
  - Configures environment and service URLs automatically
  - Sets up firewall and basic security
  - Provides next steps and useful commands reference

### Changed
- Updated environment variable structure:
  - Added production service URLs: `ML_SERVICE_URL=https://ml.c0r.ai`, `PAY_SERVICE_URL=https://pay.c0r.ai`
  - Development URLs remain: `ML_SERVICE_URL=http://ml:8001`, `PAY_SERVICE_URL=http://pay:8002`
  - Clear separation between development and production configurations
- Enhanced deployment guide:
  - Added instructions for switching between development and production URLs
  - Updated required environment variables for production
  - Improved documentation for AWS deployment process

### Fixed
- Environment configuration for production deployment on AWS
- Service URL management for different deployment environments
- Documentation clarity for production setup requirements

## [0.3.3] - 2024-07-08
### Added
- Enhanced OpenAI food analysis with detailed breakdown:
  - Individual food item detection with estimated portions
  - Weight/portion size estimation for each product (e.g., "150g", "1 cup")
  - Calories per individual food item
  - Comprehensive food analysis prompt for better accuracy
- Improved user experience in Telegram bot:
  - Detailed food breakdown display before total nutrition
  - Better formatted analysis results with emojis
  - More informative responses for users

### Changed
- Updated OpenAI Vision API integration:
  - Enhanced prompt for detailed food analysis
  - Structured JSON response with food_items array and total_nutrition
  - Better error handling and fallback values
- Improved ML service response format:
  - Returns both detailed breakdown and KBZHU summary
  - Backward compatibility with existing API consumers
- Updated photo handler to display rich food analysis:
  - Shows individual products with weights and calories
  - Maintains total KBZHU summary at the bottom
  - Better logging for debugging

### Fixed
- OpenAI response parsing for complex food analysis
- JSON structure validation for new response format
- Display formatting for detailed food breakdown

## [0.3.2] - 2024-07-08
### Changed
- Centralized routing architecture with single source of truth:
  - Created unified `common/routes.py` with all service routes defined in one place
  - Removed duplicate route files from individual services (`api.c0r.ai/app/routes.py`, `ml.c0r.ai/app/routes.py`, `pay.c0r.ai/app/routes.py`)
  - Updated all services to import routes from `common.routes.Routes`
- Improved environment variable structure:
  - Changed from full URLs to base URLs only (`ML_SERVICE_URL=http://ml:8001`, `PAY_SERVICE_URL=http://pay:8002`)
  - Route paths are now handled by centralized routing configuration
- Fixed Docker configuration issues:
  - Added missing dependencies (`loguru`, `python-multipart`) to service requirements
  - Fixed common module imports by adding proper symlinks in all Dockerfiles
  - Standardized Dockerfile structure across all services
- Updated service communication:
  - All inter-service calls now use base URL + route path pattern
  - Photo handler updated to use new routing system
  - ML service simplified to only handle file uploads (removed unused URL analysis endpoint)
- Enhanced service reliability:
  - All services now start successfully with proper dependency resolution
  - Improved error handling and logging across services
  - Fixed aiogram 3.x compatibility issues in photo processing

### Fixed
- Docker build and runtime issues with missing Python packages
- Common module import errors in ML and Payment services
- Service startup failures due to missing dependencies
- Photo upload processing with proper multipart form handling

## [0.3.1] - 2024-07-07
### Changed
- Refactored payment provider logic for maximum modularity and extensibility:
  - All Stripe-specific code and configs moved to `pay.c0r.ai/app/stripe/` (`config.py`, `client.py`)
  - All YooKassa-specific code and configs moved to `pay.c0r.ai/app/yookassa/` (`config.py`, `client.py`)
  - Each provider is now fully self-contained, making it easy to add or update providers in the future
  - Added `README.md` and `__init__.py` to each provider directory for clarity and extensibility
- Updated all imports and references in the payment service to use the new structure
- Updated root `config.py` to point to new config locations

## [0.1.1] - 2024-07-06
### Changed
- Centralized all domain and API URL logic to use `BASE_URL` from `.env`.
- Removed `NEUCOR_API_URL` from `.env` and code to avoid duplication.
- All API and payment URLs are now dynamically built from `BASE_URL`.
- Updated `.env` and code to reflect this change for easier maintenance and consistency.

## [0.1.0] - 2024-06-09
### Changed
- Full rebranding from NeuCor.AI and COR.DIET to c0r.ai across the entire project.
- Renamed all references, files, folders, and documentation:
  - NeuCor.AI → c0r.ai
  - COR.DIET → c0r.ai
  - NeuCor_Bot → c0r_ai_Bot
  - NeuCor_Service_Bot → c0r_ai_Service_Bot
  - All domains, URLs, and environment variables updated to c0r.ai
- Updated README, CONTRIBUTING, MODULES, and all code/docs to reflect new branding.

## [0.2.1] - 2024-07-07
### Added
- Implemented Supabase SQL schema for users, logs, and payments tables, with default credits = 3 and row-level security by telegram_id.
- This enables the Telegram bot to work for food analysis and testing with OpenAI and Supabase, without payment integration required for initial launch.

## [0.2.2] - 2024-07-07
### Changed
- Renamed c0r_ai_Service_Bot to c0rAIServiceBot and c0r_ai_Bot to c0rService_bot across the project for consistency.
- Added YooKassa webhook logic for Russian Telegram accounts only; Stripe is used for all other users.
- Clarified SERVICE_BOT_URL usage: this environment variable should point to the webhook endpoint of your admin/ops bot (c0rAIServiceBot) to receive payment notifications.

## [0.3.0] - 2024-07-07
### Changed
- Полный переход на монорепозиторий:
  - /api.c0r.ai/ — публичный API и Telegram-бот
  - /ml.c0r.ai/ — ML-инференс сервис
  - /pay.c0r.ai/ — платёжный сервис (модульная архитектура, YooKassa)
  - /common/ — общие утилиты, схемы, константы
  - /scripts/ — миграции, деплой, вспомогательные скрипты
- Для каждого сервиса добавлен Dockerfile
- Добавлен docker-compose.yml для локального и production запуска
- Пример nginx-конфига для проксирования поддоменов
- Удалены все тесты
- Обновлён README.md и .env.example
- Подготовлены инструкции по деплою на AWS EC2 с nginx и HTTPS
