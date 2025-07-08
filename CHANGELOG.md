# Changelog

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
### Added
- Initial project structure as per 11_STRUCTURE.md: NeuCor_Bot, Cloudflare_Worker, Payments, NeuCor_Service_Bot, n8n_Workflows directories.
- Environment variable management and validation using python-dotenv.
- Async Telegram bot skeleton using python-telegram-bot v20+.
- `/start` command: checks Supabase for user, inserts if new, returns welcome and credits info.
- `/help` command: static help text.
- Photo handler: checks credits, downloads photo, POSTs to analysis API, parses and displays KBZHU, decrements credits, shows payment link if out of credits.
- Supabase utilities: async user get/create, decrement credits, robust error handling and logging.
- User-friendly messages and inline payment button when out of credits.
- All logic is async, modular, and follows best practices for maintainability and extensibility.

## [0.2.0] - 2024-07-07
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
