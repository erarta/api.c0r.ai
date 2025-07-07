# Changelog

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
