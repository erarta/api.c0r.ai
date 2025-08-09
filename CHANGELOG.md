# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.1] - 2025-08-05

### 🚀 **MAJOR IMPROVEMENTS**

#### **Multi-LLM Provider Support**
- **Added Perplexity API integration** with `sonar` and `sonar-pro` models
- **Implemented LLM provider selection** via environment variable (`LLM_PROVIDER`)
- **Added Perplexity client** with optimized parameters for maximum accuracy
- **Enhanced provider factory** with support for OpenAI, Perplexity, and Gemini
- **Added provider info to analysis output** for debugging and transparency

#### **Advanced Food Recognition**
- **Fixed egg vs mozzarella misidentification** with aggressive prompt engineering
- **Added critical recognition rules** with specific size and texture guidelines
- **Implemented step-by-step verification** for distinguishing similar foods
- **Enhanced prompt instructions** with visual characteristics and size specifications

#### **Text Formatting Improvements**
- **Fixed text corruption issues** in positive_aspects and improvement_suggestions
- **Added flexible format handling** for both string and list responses
- **Improved message formatting** to prevent character-by-character display
- **Enhanced error handling** for malformed JSON responses

### 🔧 **TECHNICAL IMPROVEMENTS**

#### **Perplexity Integration**
- **Optimized Perplexity configuration** with temperature=0.2, top_p=0.3, presence_penalty=0.1
- **Enhanced response processing** with better JSON extraction and validation
- **Fixed streaming response handling** to prevent text corruption
- **Added provider metadata** to analysis results for transparency

#### **Enhanced Prompt Engineering**
- **Aggressive egg vs mozzarella distinction** with critical warnings and size guidelines
- **Specific visual characteristics**: eggs ~5-7 cm with yolk, mozzarella ~1-2 cm without yolk
- **Step-by-step verification process** for accurate food identification
- **Improved dish naming** to avoid generic "Analyzed Dish" responses

### 🐛 **BUG FIXES**

#### **Food Recognition**
- **Fixed persistent mozzarella misidentification** of boiled eggs with aggressive prompts
- **Resolved "Analyzed Dish" generic responses** with specific dish naming instructions
- **Corrected text formatting issues** in analysis messages
- **Fixed character-by-character display** in positive aspects and suggestions

#### **API Integration**
- **Resolved Perplexity API fallback issues** to OpenAI
- **Fixed response format handling** for streaming responses
- **Corrected JSON parsing** for mixed content responses
- **Enhanced error handling** for malformed responses

### 📊 **PERFORMANCE IMPROVEMENTS**

#### **ML Service**
- **Optimized Perplexity parameters** for maximum accuracy
- **Improved response processing** with better JSON extraction
- **Enhanced error recovery** with fallback mechanisms
- **Better logging** for debugging provider issues

#### **Text Processing**
- **Faster message formatting** with optimized string handling
- **Reduced text corruption** with improved response parsing
- **Better memory usage** with efficient JSON processing

### 🎯 **USER EXPERIENCE IMPROVEMENTS**

#### **Analysis Accuracy**
- **More precise food identification** with specific recognition rules
- **Better egg vs mozzarella distinction** using visual characteristics
- **Improved dish naming** with specific rather than generic descriptions
- **Enhanced nutritional analysis** with detailed health benefits

#### **Message Quality**
- **Cleaner text formatting** without character corruption
- **Better readability** with proper string handling
- **Provider transparency** showing which LLM was used
- **Consistent formatting** across different response types

### 🔄 **MIGRATION NOTES**

- **New environment variable**: `LLM_PROVIDER` for selecting AI provider
- **Updated prompt structure** with critical recognition rules
- **Enhanced response format** with provider metadata
- **Improved error handling** for better reliability

---

## [Unreleased] - 2025-08-09

### Added
- Mobile planning docs: `docs/mobile/` (README, PLAN, ARCHITECTURE, API_CONTRACTS, DESIGNS, REPO_STRUCTURE)
- Migration draft: `migrations/database/2025-08-09_social_feed_schema.sql` (followers, food_posts, post_likes, post_comments, conversations, messages, weight_logs with RLS policies)

### 🔧 Bug Fixes
- **Async/Await Error Fix**: Fixed "object dict can't be used in 'await' expression" error in photo analysis by removing incorrect `await` calls from synchronous functions `add_calories_from_analysis` and `get_daily_calories`
- **Calories Tracking System**: Fixed "relation 'public.daily_calories' does not exist" error by implementing proper table creation and management
- **ML Service Response Format**: Fixed "Invalid ML service response format - missing 'analysis' key" error by updating fallback logic
- **Database Connection Issues**: Fixed import errors and connection problems with Supabase client
- **Table Structure Issues**: Migrated from daily_calories_tracking view to daily_calories table for better data management and write operations
- **Telegram Entity Parsing Error**: Fixed "Missing format parameter 'progress_bar' for key 'daily_progress' in language ru" error by resolving translation key conflicts between `daily_progress` and `nutrition_daily_progress` keys
- **Language-Aware Formatting**: Replaced hardcoded Russian characters ("г", "ккал") with i18n calls in `format_analysis_result` to ensure language-aware formatting
- **OpenAI Response Parsing**: Fixed JSON parsing errors by simplifying ML service prompts to avoid content filtering issues and improve response reliability
- **Prompt Simplification**: Reduced complex prompts to simple, direct instructions to avoid OpenAI content filtering and improve response reliability
- **Temperature Adjustment**: Changed OpenAI model temperature from 0.1 to 0.3 for better response creativity and reduced content filtering
- **Complete System Rebuild**: Performed full Docker rebuild with --no-cache to ensure all configuration changes are properly applied
- **Full Clean Rebuild**: Performed complete system rebuild with docker-compose down, docker system prune, and fresh --no-cache build to ensure all changes are properly applied and cached issues are resolved
- **Creative Success Headers**: Replaced duplicate static "Amazing! Your results are ready!" headers with 12 creative randomized headers for both English and Russian to provide variety and better user experience
- **Random Header System**: Added get_random_header() function to i18n manager for selecting creative headers from arrays, enhancing user engagement with diverse messaging
- **Enhanced Food Recognition Accuracy**: Improved prompts with detailed visual recognition rules to distinguish eggs from cheese and other similar food items
- **Precise Weight Estimations**: Added realistic portion size guidelines (egg=50-60g, cheese=20-40g) to improve calorie calculation accuracy
- **Advanced Visual Analysis**: Enhanced system prompt for expert-level food identification with focus on shape, color, texture, and size details
- **Temperature Optimization**: Increased model temperature from 0.3 to 0.4 for better food recognition flexibility while maintaining accuracy
- **Hot-Reload Development Setup**: Implemented docker-compose.override.yml with volume mounting for instant code changes without container rebuilds  
- **Development Mode Script**: Added scripts/dev-mode.sh for fast development workflow with automatic service health checks
- **Critical Recognition Rules**: Enhanced prompts with explicit egg vs cheese distinction and mandatory visual checks to prevent misidentification
- **Import Path Fix**: Corrected relative imports in profile.py and main.py for utils modules to use full package paths for proper module resolution
- **Aggressive Egg Recognition**: Increased temperature to 0.7 and implemented highly aggressive prompts with explicit warnings against calling eggs mozzarella  
- **Ultra-Specific Visual Rules**: Added step-by-step food identification process with emphasis on yolk detection for proper egg vs cheese classification
- **Multi-LLM Provider Support**: Implemented LLM provider factory with support for OpenAI, Perplexity, and Gemini via LLM_PROVIDER environment variable
- **Shared Prompts System**: Extracted food analysis prompts to shared module for consistent behavior across all LLM providers 
- **Perplexity Integration**: Added Perplexity API client using llama-3.1-sonar-large-128k-online model for potentially better food recognition
- **LLM Debug Output**: Added llm_provider and model_used fields to analysis output for debugging and transparency
- **Clean Prompts**: Removed aggressive hints and leading prompts for fair comparison between LLM providers
- **LLM Provider in Header**: Added LLM provider display in analysis header (e.g., "🤖 Анализ: Perplexity Llama-3.1")
- **Perplexity Vision Support**: Fixed Perplexity model to use 'sonar' and 'sonar-pro' which DO support vision analysis (not sonar-deep-research)
- **Gemini Shared Prompts**: Updated Gemini client to use shared prompts and added debug information
- **Food Facts System**: Added 300+ interesting food facts in Russian and English, shown randomly during analysis
- **Creative Waiting Phrases**: Added 50 creative and fun waiting phrases for analysis process
- **Perplexity Precision Tuning**: Optimized Perplexity API parameters (temperature=0.2, top_p=0.5) for better food recognition accuracy
- **Detailed Analysis Restoration**: Restored comprehensive food analysis formatting with regional dish identification, detailed nutrition breakdown, health scores, and improvement suggestions
- **Daily Progress Fix**: Fixed daily calories tracking to display progress AFTER adding new calories, and corrected progress bar formatting key from 'daily_progress' to 'daily_progress_bar'
- **Payment System Fix**: Fixed payment button functionality by correcting i18n import in payments handler from 'from i18n import i18n' to 'from i18n.i18n import i18n' and performing full container restart to clear cache
- **Translation Key Separation**: Created separate `nutrition_daily_progress` key for nutrition analysis to avoid conflicts with daily progress tracking
- **Pydantic v2 Compatibility**: Updated all models to use `pattern` instead of `regex` in Field definitions for Pydantic v2 compatibility
- **Test Infrastructure Fixes**: Fixed import paths, mocking strategies, and assertion updates for comprehensive test coverage
- **Unit Test Coverage**: Fixed 97 unit tests across commands, health checks, shared models, and nutrition calculations
- **Import Path Corrections**: Updated import paths to reflect current project structure
- **Test Mocking**: Corrected mock targets and parameters for external dependencies
- **Validation Error Handling**: Updated test expectations for Pydantic v2 validation errors

### 📈 Stability & Ops
- **Bot Rate Limiter**: Added periodic cleanup for in-memory rate-limit buckets to prevent unbounded growth over long uptimes
- **OpenAI Calls**: Offloaded sync OpenAI SDK requests to a background thread to avoid event loop blocking under load
- **Docker Runtime**: Added memory reservations/limits and JSON log rotation for `api`, `ml`, and `pay` services in `docker-compose.yml` (also included non-swarm `mem_limit`/`mem_reservation` for docker-compose)

### ✨ New Features
- **CaloriesService Module**: Created dedicated module for calorie tracking with automatic table creation
- **Comprehensive Unit Tests**: Added 15+ unit tests for calories management system
- **Enhanced Error Handling**: Improved error messages and logging throughout the system
- **Database Schema Management**: Added SQL scripts for table creation and migration
- **Data Migration System**: Added script to migrate data from daily_calories_tracking view to daily_calories table

### ⚠️ Deployment Note
- **Production Deployment Required**: The Telegram entity parsing error fix requires deployment to production environment. The local code changes are correct, but the production environment may still be running the old code causing the "Missing format parameter 'progress_bar' for key 'daily_progress' in language ru" error.

### 📝 Technical Details
- **Files Modified**: 
  - `services/api/bot/handlers/photo.py` - Updated to use `nutrition_daily_progress` key
  - `i18n/en/nutrition.py` - Added `nutrition_daily_progress` translation
  - `i18n/ru/nutrition.py` - Added `nutrition_daily_progress` translation
  - All Pydantic model files - Updated `regex` to `pattern`
  - All test files - Fixed imports, mocks, and assertions
- **Translation Keys**: Separated `daily_progress` (for daily tracking) from `nutrition_daily_progress` (for nutrition analysis)
- **Test Results**: All 97 unit tests passing, integration tests require environment variables

---

## Archive

For older changelog entries, see the organized files in the [`changelogs/`](changelogs/) directory:

- [`changelogs/v0.4.x.md`](changelogs/v0.4.x.md) - Version 0.4.x changes (0.4.0 - 0.4.2) - **ML Service Enhancements & Photo Analysis Improvements**
- [`changelogs/v0.3.x.md`](changelogs/v0.3.x.md) - Version 0.3.x changes (0.3.0 - 0.3.68)
- [`changelogs/v0.2.x.md`](changelogs/v0.2.x.md) - Version 0.2.x changes  
- [`changelogs/v0.1.x.md`](changelogs/v0.1.x.md) - Version 0.1.x changes
- [`changelogs/v0.0.x.md`](changelogs/v0.0.x.md) - Version 0.0.x changes

## Contributing

When adding new changes:
1. Add entries directly to the appropriate version file in `changelogs/` directory
2. Keep the main `CHANGELOG.md` clean - only update archive links when needed
3. Follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format
4. Use categories: Added, Changed, Deprecated, Removed, Fixed, Security
