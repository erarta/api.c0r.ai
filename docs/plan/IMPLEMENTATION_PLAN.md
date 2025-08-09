# Implementation Plan (v0.1.0)

Date: 2025-08-09
Owner: Engineering
Status: Active

---

## 1. Scope and Objectives

- Implement label analyze API skeleton with OCR/barcode pipeline (upgradeable from stubs).
- Extend Telegram bot profile flow (preferences, allergies, goals) and reuse across mobile app.
- Add favorites and saved recipes endpoints with strict request/response models.
- Provide DB migrations + rollback, i18n, docs, and comprehensive tests.
- Enable API access for mobile clients (CORS + auth strategy).

---

## 2. Architecture Overview

- Services:
  - `services/ml/`: FastAPI app for analysis, label OCR/barcode, LLM analysis.
  - `services/api/bot/`: FastAPI app + Telegram bot handlers for user flows.
  - `services/pay/`: Payment integrations (Stripe/YooKassa).
- Shared:
  - `common/`: routes, DB modules, auth middleware, etc.
  - `shared/`: health checks, auth decorators, region detection.
- External dependencies:
  - LLM providers (OpenAI/Perplexity/Gemini) for food analysis (not for barcode decoding).
  - OCR/Barcode libraries for label scanning.

---

## 3. Endpoints (Current + Planned)

### 3.1 ML Service
- `POST /api/v1/label/analyze`
  - Auth: Internal (X-Internal-Token) currently. Consider public facade via API gateway for mobile.
  - Form-data: `photo` (image), `user_language` (en|ru, default en)
  - Response (skeleton): barcodes[], ocr_text, ocr_blocks[], notes.
  - Planned: add `nutrition` object with parsed nutrition facts and provenance.

### 3.2 API Service (Favorites & Recipes)
- `POST /favorites/save` → `FavoritesSaveRequest` → `FavoriteResponse`
- `GET /favorites/list?user_id=...&limit=...&search=...` → `FavoritesListResponse`
- `GET /favorites/{favorite_id}?user_id=...` → `FavoriteResponse`
- `DELETE /favorites/{favorite_id}?user_id=...` → `OkResponse`
- `POST /recipes/save` → `RecipesSaveRequest` → `RecipeResponse`
- `GET /recipes/list?user_id=...&limit=...&search=...` → `RecipesListResponse`
- `GET /recipes/{recipe_id}?user_id=...` → `RecipeResponse`
- `DELETE /recipes/{recipe_id}?user_id=...` → `OkResponse`
- Auth: currently `@require_internal_auth` for service-to-service. See Section 7 for mobile strategy.

### 3.3 Swagger/OpenAPI
- Each FastAPI app exposes `/docs` and `/openapi.json`.
- Models added for favorites/recipes to improve schema.

---

## 4. Migrations and Order

- Run forward migrations in chronological order by filename timestamp.
- Apply next: `migrations/database/2025-08-08_features_favorites_plans_recipes.sql`.
- Rollback, if needed: `migrations/database/2025-08-08_features_favorites_plans_recipes_rollback.sql`.
- Rule: multiple files for the same date → run lexicographically.

---

## 5. CORS and Mobile Access

- `services/api/bot/main.py` and `services/ml/main.py` use `CORSMiddleware`.
- Env: `CORS_ORIGINS` (comma-separated). Default `*` (development only).
- Mobile access strategies:
  - A) API Gateway / BFF authenticates users (JWT/OAuth), injects internal token to protected internal routes.
  - B) Add user-level auth directly on mobile-facing endpoints and remove `@require_internal_auth` for those. Requires JWT issuance and verification.

---

## 6. OCR/Barcode Pipeline (Production)

- Barcode:
  - Libraries: `pyzbar` (ZBar) or `zxing` (ZXing).
  - Preprocess: grayscale, CLAHE, denoise, adaptive threshold; decode at multiple scales.
  - Accept EAN-13/8, UPC-A/E, QR, Code128; validate EAN/UPC checksums; dedupe by (type,data).
  - If EAN/UPC found, optional lookup in OpenFoodFacts/GS1.
- OCR:
  - Libraries: `pytesseract` (requires tesseract binary + lang packs) or `easyocr` (no system binary).
  - Preprocess: grayscale, Otsu/adaptive threshold, deskew via contour/lines; retry with variants.
  - Extract words/boxes and confidence; support multi-lang (e.g., `eng+rus`).
- Nutrition Table Parsing:
  - Detect table region via contours/Hough lines; perspective transform.
  - Parse per-line or per-grid; map aliases (energy/fat/saturates/carbs/sugars/protein/salt; multilingual).
  - Normalize units (kJ↔kcal, g/mg/µg) and sodium↔salt conversion if needed.
  - Provide per_100g and per_serving; parse serving size.
  - Confidence scores; provenance (ocr vs db).
- LLM usage: optional post-processor for text normalization only, not numeric extraction.

---

## 7. Authentication

- Internal: `@require_internal_auth` and `X-Internal-Token` for inter-service calls.
- Mobile/Web:
  - Option A (preferred): API gateway that terminates user auth and forwards to internal endpoints with internal token.
  - Option B: add JWT-based user auth to favorites/recipes (and future public label analyze) endpoints directly in API service.

---

## 8. Pydantic Models (API)

- Favorites:
  - Requests: `FavoritesSaveRequest` {user_id, name, items_json, composition_hash, default_portion?}
  - Responses: `FavoriteItem`, `FavoriteResponse`, `FavoritesListResponse`, `OkResponse`.
- Recipes:
  - Requests: `RecipesSaveRequest` {user_id, title, recipe_json, language?, source?}
  - Responses: `RecipeItem`, `RecipeResponse`, `RecipesListResponse`, `OkResponse`.

---

## 9. i18n

- Profile and bot flows use i18n keys (preferences, allergies, goals, prompts).
- Action: audit `i18n/` to ensure all keys referenced in `services/api/bot/handlers/profile.py` exist; add missing keys.
- Label analyze endpoint returns technical fields; no UI copy required.

---

## 10. Testing Strategy

- Unit tests (added):
  - ML label analyze skeleton auth and success.
  - LLM provider override behavior in factory.
  - API routes presence for favorites/recipes.
- Unit tests (planned):
  - Favorites/recipes endpoints using `TestClient` with mocked `common.supabase_client` DB calls.
  - i18n key audit script/test to fail on missing keys.
  - OCR/barcode pipeline with synthetic images to cover decoding and parsing branches.
- Integration tests (planned):
  - End-to-end analyze → save favorite → list/delete; profile flow end-to-end (Telegram bot mocked where possible).

---

## 11. Dependencies

- Core: FastAPI, Pydantic, httpx, loguru.
- OCR/Barcode (planned): `opencv-python`, `pyzbar` or `zxing`, `pytesseract` or `easyocr`.
- System (if pytesseract): tesseract binary + language packs.
- Testing: pytest, pytest-asyncio, requests, fastapi TestClient.

---

## 12. Environment Variables

- `INTERNAL_API_TOKEN`: inter-service auth.
- `CORS_ORIGINS`: comma-separated allowed origins.
- `ML_SERVICE_URL`, `PAY_SERVICE_URL`: service base URLs.
- `LLM_PROVIDER`, `ANALYSIS_PROVIDER`: default provider selection; can override per request.
- OCR/Barcode flags (future): `OCR_PROVIDER`, `BARCODE_PROVIDER`, feature flags for pipeline steps.

---

## 13. Changelog Policy

- Start from `changelogs/CHANGELOG_v0.1.0.md`.
- Each version increments with semantic versioning; do not remove historical files.
- Summarize Added/Changed/Fixed/Notes with dates.

---

## 14. Rebranding Note

- Project rebranding to AIDI.APP is planned. Post v0.1.0, audit:
  - Service names, i18n/user-facing strings, README/docs, and domain references.
  - Maintain microservice boundaries.

---

## 15. Roadmap and Milestones

- v0.1.0 (current):
  - Label analyze skeleton, favorites/recipes endpoints with models, CORS, migrations+rollback, baseline tests, changelog.
- v0.1.1:
  - Add tests for favorites/recipes (mocked DB), i18n audit script, docs for mobile auth strategy.
- v0.2.0:
  - Implement OCR/barcode pipeline (pyzbar/easyocr + OpenCV), nutrition parsing with confidence, OpenFoodFacts integration.
- v0.2.1:
  - Public/mobile-safe endpoints (JWT) or gateway setup; profile taste preferences; meal plan trigger logic.
- v0.3.x:
  - Meal planning (duration flexibility 2–3 days/weeks), groceries integration by region; recipe save/quick-add UX.

---

## 16. Acceptance Criteria (v0.1.0)

- ML `/api/v1/label/analyze` exists, secured via internal auth, returns structured stubs.
- API favorites/recipes endpoints return responses per Pydantic models.
- Migrations up and rollbacks available.
- CORS enabled; Swagger accessible.
- Tests pass for current scope (skeleton, provider override, route presence).

---

## 17. Open Questions

- Choose mobile auth approach (gateway vs direct JWT on endpoints).
- Preferred OCR/Barcode stack (`pytesseract` vs `easyocr`, `pyzbar` vs `zxing`).
- OpenFoodFacts/GS1 integration priority and API keys.
