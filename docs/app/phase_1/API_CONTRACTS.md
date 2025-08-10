# App Phase 1 — API Contracts

All endpoints require `Authorization: Bearer <Supabase JWT>`.

## Analyze (common)
- POST `/v1/analyze`
  - multipart: `photo` (image), `provider?`, `user_language?`
  - Response: `{ analysis: {...}, daily_summary: {...} }`

## Tracker
- GET `/v1/app/daily?date=YYYY-MM-DD`
- GET `/v1/app/progress?range=7|30|90|365`
- GET `/v1/app/history?cursor=...&limit=...`

## Favorites & Recipes
- POST `/v1/app/favorites`
- GET `/v1/app/favorites?limit=..&search=..`
- GET `/v1/app/favorites/{id}`
- DELETE `/v1/app/favorites/{id}`
- Same for `/v1/app/recipes`

## Weight Logs
- POST `/v1/app/weight-logs` { date, weight_kg }
- GET `/v1/app/weight-logs?range=...`

## Barcode/Label
- POST `/v1/app/label/analyze`
