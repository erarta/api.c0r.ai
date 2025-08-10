# App Phase 1 — Plan (Tracker MVP)

- Onboarding (4–6 screens) → `profiles`
- Auth: Supabase (email, Google, Apple)
- Home: `daily_calories` + recent `logs`
- Analyze: POST `/v1/analyze` (1 credit) → updates `logs` and `daily_calories`
- History: GET `/v1/app/history`
- Favorites/Recipes: `/v1/app/favorites/*`, `/v1/app/recipes/*`
- Progress + `weight_logs`: `/v1/app/progress`, `/v1/app/weight-logs`
- Barcode/Label: `/v1/app/label/analyze` (stub ok; OFF later)
- Payments: YooKassa in MVP; IAP later
