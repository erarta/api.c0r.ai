# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **Recipe Generation ML Service Communication**: Fixed 422 error in ML service communication for recipe generation
  - Corrected `telegram_user_id` field to send actual Telegram user ID instead of database user ID
  - Fixed missing required fields (`image_url`, `telegram_user_id`, `user_context`) in ML service request payload
  - Recipe generation from photos now works correctly with proper service communication

### Added
- **Test Suite Refactoring**: Comprehensive test infrastructure improvements for better maintainability and coverage
  - **Modular FSM Tests**: Split large `test_fsm_state_management.py` (534 lines) into 4 focused modules:
    - `tests/unit/test_fsm_basic_operations.py` - Basic FSM state operations and transitions (120 lines)
    - `tests/unit/test_fsm_nutrition_flow.py` - Nutrition analysis workflow tests (150 lines)
    - `tests/unit/test_fsm_recipe_flow.py` - Recipe generation workflow tests (150 lines)
    - `tests/unit/test_fsm_error_handling.py` - FSM error handling and edge cases (170 lines)
  - **Shared Test Infrastructure**: Centralized test utilities and fixtures
    - `tests/test_utils.py` - Standardized import path setup for all tests
    - `tests/shared_fixtures.py` - Common fixtures for FSM, user data, and ML responses (125 lines)
    - `tests/base_test_classes.py` - Base test classes with common functionality (70 lines)
    - `tests/conftest.py` - Global test configuration with environment setup
    - `tests/.env.test` - Test-specific environment variables
  - **External Service Mocks**: Comprehensive mocking system for integration tests
    - `tests/mocks/external_services.py` - Mock implementations for Supabase, YooKassa, ML service, Telegram bot, and R2 storage (170 lines)
    - `tests/integration/test_payment_integration.py` - Proper integration tests with mocking (220 lines)
  - **AsyncMock Configuration Fixes**: Resolved AsyncMock-related test failures with proper async fixture setup
  - **Standardized Import Paths**: Unified import path management across all test files using `setup_test_imports()`
  - **Enhanced Test Documentation**: Comprehensive test suite documentation in `tests/README.md` (200 lines)
- **Database Migration System**: Complete migration tracking and management system
  - `migrations/database/2025-01-26_schema_migrations.sql` - Migration tracking table with checksums and rollback support
  - `scripts/run_migrations.py` - Automated migration runner with Supabase integration (200 lines)
  - Automatic migration detection and execution with duplicate prevention
  - Rollback capability with corresponding rollback scripts
- **Deployment Notification System**: Automated deployment status reporting
  - `scripts/deploy_notifications.py` - Telegram bot integration for deployment notifications (180 lines)
  - Success/failure notifications with detailed error reporting
  - Integration with service bot for deployment monitoring
- **Modular i18n Translation System**: Restructured translation files for better maintainability
  - Split large English translation file (629 lines) into 8 focused modules:
    - `i18n/en/welcome.py` - Welcome messages and onboarding
    - `i18n/en/help.py` - Help system and commands
    - `i18n/en/profile.py` - Profile management and setup
    - `i18n/en/payments.py` - Payment processing messages
    - `i18n/en/errors.py` - Error messages and validation
    - `i18n/en/nutrition.py` - Nutrition analysis and calculations
    - `i18n/en/daily.py` - Daily tracking and logging
    - `i18n/en/recipes.py` - Recipe generation and management
    - `i18n/en/reports.py` - Report generation and analytics
  - Updated `i18n/i18n.py` with modular loading and fallback support
  - Started Russian translation modularization with `i18n/ru/welcome.py`
- **Deployment Documentation**: Comprehensive production deployment guide with migration procedures in `docs/deployment/production-deployment.md`
- **Deployment Q&A**: Detailed answers to common deployment questions in `docs/deployment/deployment-qa.md`

### Changed
- **Code Organization**: Refactored `common/supabase_client.py` into modular structure under `common/db/`
- **Payment Configuration**: Centralized payment plans configuration in `common/config/payment_plans.py`
- **Changelog Organization**: Split large changelog into organized version-specific files in `changelogs/` directory
- **Migration System**: Organized database migrations into structured `/migrations` directory with proper categorization
- **Project Structure**: Cleaned up root directory by removing unused files and organizing utilities
- **Service Architecture**: Reorganized entire codebase into modular service architecture under `/services`
- **Health Endpoints**: Standardized health check responses using shared `create_health_response()` function
- **Translation Architecture**: Moved from monolithic translation files to modular, maintainable structure

### Removed
- **Duplicate Code Elimination**: Removed `Cloudflare_Worker/` directory as functionality was already migrated to `services/api/edge/`
- **Old Migration Files**: Cleaned up root directory migration files that were moved to structured `/migrations` system

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

---

## Archive

For older changelog entries, see the organized files in the [`changelogs/`](changelogs/) directory:

- [`changelogs/v0.3.x.md`](changelogs/v0.3.x.md) - Version 0.3.x changes (0.3.0 - 0.3.62)
- [`changelogs/v0.2.x.md`](changelogs/v0.2.x.md) - Version 0.2.x changes  
- [`changelogs/v0.1.x.md`](changelogs/v0.1.x.md) - Version 0.1.x changes
- [`changelogs/v0.0.x.md`](changelogs/v0.0.x.md) - Version 0.0.x changes

## Contributing

When adding new changes:
1. Add entries to the `[Unreleased]` section during development
2. Move entries to a new version section when releasing
3. Follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format
4. Use categories: Added, Changed, Deprecated, Removed, Fixed, Security
