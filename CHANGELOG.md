# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- **Code Organization**: Refactored `common/supabase_client.py` into modular structure under `common/db/`
- **Payment Configuration**: Centralized payment plans configuration in `common/config/payment_plans.py`
- **Changelog Organization**: Split large changelog into organized version-specific files in `changelogs/` directory
- **Migration System**: Organized database migrations into structured `/migrations` directory with proper categorization
- **Project Structure**: Cleaned up root directory by removing unused files and organizing utilities
- **Service Architecture**: Reorganized entire codebase into modular service architecture under `/services`
- **Health Endpoints**: Standardized health check responses using shared `create_health_response()` function

### Added
- **Modular Service Architecture**: New service-based organization:
  - `services/api/bot/` - Telegram Bot (from api.c0r.ai)
  - `services/api/edge/` - Edge API (from Cloudflare_Worker)
  - `services/ml/openai/` - OpenAI integration
  - `services/ml/gemini/` - Gemini integration
  - `services/pay/stripe/` - Stripe integration with webhooks
  - `services/pay/yookassa/` - YooKassa integration
- **Shared Components**: Inter-service contracts and utilities in `/shared` directory
- **Service Documentation**: Comprehensive README files for each service and component

### Removed
- **Unused Code Cleanup**: Removed 17 unused files (~3,598 lines of code):
  - 8 temporary test scripts (check_bot_payments.py, fix_incomplete_profiles.py, run_bot_test.py, etc.)
  - 7 old migration files replaced by structured system (database_*.sql, migration_*.sql, schema.sql)
  - Moved 2 useful utilities to `/scripts/` directory (run_multilingual_migration.py, monitor_bot.sh)
- **Duplicate Code Elimination**: Major code deduplication completed:
  - Removed `Payments/` directory (duplicated pay.c0r.ai functionality)
  - Removed old service directories: `api.c0r.ai/`, `pay.c0r.ai/`, `ml.c0r.ai/` (100% duplicated by new `/services` structure)
  - Removed duplicate Stripe webhook handler from `services/pay/main.py` (full implementation exists in `services/pay/stripe/webhooks.py`)
  - Eliminated duplicate health endpoint implementations across services

### Added
- **Modular Database Operations**: New modular structure for database operations:
  - `common/db/client.py` - Supabase client initialization
  - `common/db/users.py` - User management operations
  - `common/db/profiles.py` - Profile and calorie calculation operations
  - `common/db/logs.py` - Action logging operations
  - `common/db/payments.py` - Payment operations
- **Centralized Configuration**: Environment-aware payment plans configuration
- **Backward Compatibility**: Legacy support layer for existing imports
- **Migration System**: Structured database migration system:
  - `migrations/database/` - Timestamped migration files
  - `migrations/rollbacks/` - Rollback scripts for each migration
  - `migrations/schema/` - Complete database schema for fresh installations
  - `migrations/README.md` - Comprehensive migration system documentation
- **Shared Components**: Common functionality to eliminate code duplication:
  - `shared/health.py` - Standardized health check response generator for all services
  - `shared/auth/` - Centralized inter-service authentication system
- **Phase 3.3 - Health Check Endpoints**: Comprehensive service monitoring system
  - Enhanced `shared/health.py` with advanced dependency checking:
    - Database connectivity validation (Supabase)
    - External service availability checks
    - OpenAI API connectivity validation
    - Configurable timeout and error handling
  - Updated all service health endpoints with comprehensive monitoring:
    - API Service: Database + external services (ML, Payment) + R2 status
    - ML Service: Database + OpenAI API + provider configuration status
    - Payment Service: Database + API service + payment provider status
  - Added standardized health response format with dependency details:
    - Service status levels: `healthy`, `degraded`, `unhealthy`
    - Response time metrics for all dependencies
    - Detailed error reporting and configuration status
  - Created extensive test coverage (535 lines total):
    - Unit tests for health check functionality
    - Integration tests for all service endpoints
  - Complete documentation in `docs/development/health-checks.md`
- **Phase 3.2 - API Contracts & Pydantic Models**: Complete inter-service contract system
  - Created comprehensive Pydantic models in `shared/models/`:
    - `common.py` - Base response models and error handling
    - `user.py` - User profiles, requests, and credit management
    - `nutrition.py` - Food analysis and nutrition data models
    - `payment.py` - Payment processing and invoice models
    - `ml.py` - ML service requests and responses
  - Implemented service contracts in `shared/contracts/`:
    - `api_ml.py` - API ↔ ML service contract with validation
    - `api_pay.py` - API ↔ Payment service contract
    - `ml_pay.py` - ML ↔ Payment service contract (future features)
  - Added comprehensive validation with custom validators
  - Created extensive test coverage (588 lines total):
    - Unit tests for all Pydantic models
    - Integration tests for service contracts
  - Complete documentation in `docs/development/api-contracts.md`
- **Phase 3.1 - Service Authentication System**: Complete inter-service authentication implementation
  - Created centralized authentication module in `shared/auth/`
  - `@require_internal_auth` decorator for protecting internal endpoints
  - `get_auth_headers()` function for standardized outgoing requests
  - Token validation middleware with security logging
  - Updated all three services (API, ML, Payment) with authentication
  - Protected endpoints: `/credits/add`, `/analyze`, `/recipe`, `/invoice`
  - Comprehensive unit and integration tests (291 lines total)
  - Complete documentation in `docs/development/service-authentication.md`
- **Service Authentication**: Comprehensive API key-based authentication system:
  - `@require_internal_auth` decorator for protecting internal endpoints
  - `get_auth_headers()` function for standardized outgoing requests
  - Token validation and security logging
  - Protection for all inter-service communication endpoints
- **Documentation**: Comprehensive documentation for new configuration and migration systems
- **Security**: Enhanced inter-service security with mandatory authentication

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

## [0.3.56] - 2025-07-20

### Fixed
- **Profile Display Enhancement**: Added dietary preferences and allergies information to profile display
- **Profile Display Translation**: All profile fields now show translated values instead of English codes
- **Profile Display Format**: Fixed duplicate emojis and units in profile display (e.g., "👨 👨 Мужской", "170 см см")
- **Macro Distribution Error**: Fixed KeyError 'protein_g' in nutrition section by correcting data structure access
- **Payment Service Error**: Added proper error handling for ServerDisconnectedError in payment processing
- **Payment Error Translation**: Added Russian translation for payment service unavailable message

### Added
- **Profile Display Sections**: Added dedicated sections for dietary preferences and allergies in profile display
- **Translation Keys**: Added new translation keys for profile display enhancements
- **Error Handling**: Enhanced error handling for payment service connectivity issues

## [0.3.54] - 2025-07-20

### Fixed
- **Profile Setup Translation**: Fixed UnboundLocalError in `process_age` and `process_goal` functions where `user_language` variable was not defined
- **Telegram Markdown Error**: Fixed TelegramBadRequest "can't parse entities" error by removing `parse_mode="Markdown"` from messages containing emojis
- **Profile Setup Flow**: Ensured all profile setup steps use proper Russian translations with emoji support

### Added
- **Enhanced Translations**: Added comprehensive Russian translations for all profile setup steps
- **Emoji Support**: Added emoji indicators for better user experience in profile setup
- **Error Handling**: Improved error handling for Telegram message formatting issues

---

## Archive

For older changelog entries, see the organized files in the [`changelogs/`](changelogs/) directory:

- [`changelogs/v0.3.x.md`](changelogs/v0.3.x.md) - Version 0.3.x changes
- [`changelogs/v0.2.x.md`](changelogs/v0.2.x.md) - Version 0.2.x changes  
- [`changelogs/v0.1.x.md`](changelogs/v0.1.x.md) - Version 0.1.x changes
- [`changelogs/v0.0.x.md`](changelogs/v0.0.x.md) - Version 0.0.x changes

## Contributing

When adding new changes:
1. Add entries to the `[Unreleased]` section during development
2. Move entries to a new version section when releasing
3. Follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format
4. Use categories: Added, Changed, Deprecated, Removed, Fixed, Security
