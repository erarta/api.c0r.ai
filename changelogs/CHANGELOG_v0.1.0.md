# Changelog v0.1.0 (2025-08-09)

## Added
- ML: POST /api/v1/label/analyze skeleton with Pydantic models and internal auth; OCR/barcode stubs.
- API: Favorites and Recipes endpoints with Pydantic request/response models.
- Security: Internal auth enforced for inter-service endpoints; CORS enabled via CORS_ORIGINS env.
- Docs: README_endpoints_and_providers describing endpoints, provider envs, migrations.
- Migrations: 2025-08-08_features_favorites_plans_recipes.sql + rollback file.
- Tests: label analyze endpoint (skeleton), provider override factory, API routes presence.

## Changed
- Profile flow in Telegram bot validated to support preferences, allergies, goals, with i18n.

## Notes
- Barcode/OCR are stubbed; production plan: pytesseract/easyocr and pyzbar/zxing.
- OpenAPI docs available at /docs for API and ML services.
