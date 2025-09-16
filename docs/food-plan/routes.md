Food Plan API Routes

Base router: services/api/public/routers/meal_plan.py

POST /food-plan/generate
- Body: { days: int (1..7) }
- Auth: AuthContext (dev shim: X-User-ID header)
- Flow: context → unlock check → LLM generate → compute totals → upsert → return plan

POST /food-plan/generate-internal
- Body: { user_id: string, days: int (1..7) }
- Auth: X-Internal-Token
- Same flow; explicit user_id for internal calls

GET /food-plan/current
- Auth: AuthContext
- Returns plan covering today, or latest plan

GET /food-plan/current-internal?user_id=...
- Auth: X-Internal-Token
- Returns plan covering today, or latest plan for user

GET /food-plan/unlock-status-internal?user_id=...
- Auth: X-Internal-Token
- Returns { unlocked, subscribed, total_analyses_14d, active_days_14d }

Smoke tests
1) Generate (internal):
curl -X POST "http://localhost:8000/food-plan/generate-internal" \
  -H "Content-Type: application/json" \
  -H "X-Internal-Token: $INTERNAL_API_TOKEN" \
  -d '{"user_id":"<USER_UUID>","days":3,"force":true}'

2) Get current (internal):
curl -s "http://localhost:8000/food-plan/current-internal?user_id=<USER_UUID>" \
  -H "X-Internal-Token: $INTERNAL_API_TOKEN"

