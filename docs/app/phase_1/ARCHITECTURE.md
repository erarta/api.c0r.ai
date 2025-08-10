# App Phase 1 — Architecture

- Client: Flutter (Dart)
  - Auth: supabase_flutter (email, Google, Apple)
  - Network: dio
  - State: riverpod
  - Media: camera/image_picker, mobile_scanner (barcode)
  - Charts: fl_chart
- Backend: existing Python services (API/ML/Pay) on EC2
- Database: Supabase Postgres (RLS) + R2 for images

## Key flows
- Analyze (1 credit):
  - App → API `/v1/analyze` (photo)
  - API validates Supabase JWT → calls ML analyze → decrements credit → writes `logs`, `daily_calories` → returns analysis + updated daily summary
- Favorites/Recipes:
  - App → API `/v1/app/favorites/*`, `/v1/app/recipes/*` (proxy to internal endpoints)
- Progress & History:
  - App → API `/v1/app/daily`, `/v1/app/progress`, `/v1/app/history`
- Barcode/Label:
  - App → API `/v1/app/label/analyze` (stub ok)
- Payments:
  - YooKassa hosted checkout → webhook → add credits

## Security
- Mobile sends Supabase JWT; API verifies via Supabase JWKS
- Internal services remain protected with internal token; only API calls them
- RLS protects user-owned data (`weight_logs`, `daily_calories`)
