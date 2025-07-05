# Changelog

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
