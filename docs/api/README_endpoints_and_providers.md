# API and ML Endpoints (Aug 8, 2025)

This doc summarizes new endpoints and provider configuration.

## ML Service

- POST `/api/v1/analyze`
  - Analyze food photo via selected LLM provider.
  - Form fields: `photo` (image), `user_language` (default: `en`), `provider` (optional override).

- POST `/api/v1/generate-recipe`
  - Generate recipe from analysis context.

- POST `/api/v1/label/analyze` (NEW)
  - Skeleton label/packaging analysis.
  - Auth: internal.
  - Form fields: `photo` (image), `user_language` (default: `en`).
  - Response: `{ language, barcodes[], ocr_text, ocr_blocks[], parsed_nutrition, notes }`.

- GET `/` or `/health`
  - Health and provider diagnostics.

### Provider selection

- Environment variables:
  - `LLM_PROVIDER`: `openai|perplexity|gemini` (others as integrated)
  - `ANALYSIS_PROVIDER`: alias for the same. If both set, `ANALYSIS_PROVIDER` wins inside analysis contexts.
- Per request override:
  - `provider` form field on `POST /api/v1/analyze`.
- The effective provider is echoed in results when possible.

## API (Bot) Service

- Favorites (NEW)
  - POST `/favorites/save`
  - GET `/favorites/list?user_id=<uuid>&limit=20&search=...`
  - GET `/favorites/{id}`
  - DELETE `/favorites/{id}`

- Recipes (NEW)
  - POST `/recipes/save`
  - GET `/recipes/list?user_id=<uuid>&limit=20&search=...`
  - GET `/recipes/{id}`
  - DELETE `/recipes/{id}`

All above endpoints require internal authentication.

## Database Migrations

- Forward: `migrations/database/2025-08-08_features_favorites_plans_recipes.sql`
  - Creates: `favorites_food`, `analysis_corrections`, `meal_plans`, `saved_recipes` and indexes.
- Rollback: `migrations/database/2025-08-08_features_favorites_plans_recipes_rollback.sql`
  - Drops all objects created by forward migration.

## i18n

- New UI copy for profile and flows should be added under `i18n/` keys. The label analyze endpoint currently returns technical fields without user-facing strings.

## Testing

- Planned: unit tests for provider overrides, label endpoint skeleton, and DB modules using mocks.
