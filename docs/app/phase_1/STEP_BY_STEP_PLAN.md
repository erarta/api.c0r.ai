# Phase 1 — Step-by-step Plan (with design anchors)

Screenshots live under `docs/app/phase_1/DESIGNS/`.

## 1. Onboarding (4–6 screens) + Auth
- Supabase Auth (email, Google, Apple)
- Onboarding quiz -> save to `profiles`
- Designs:
  - ![Onboarding](./DESIGNS/onboarding_quiz.png)
  - ![Auth](./DESIGNS/auth.png)

## 2. Home (Today)
- Fetch `daily_calories` for today and recent `logs`
- Designs:
  - ![Home Today](./DESIGNS/home_today.png)

## 3. Capture → Analyze
- Camera or gallery upload
- Call `/v1/analyze` (1 credit), update `logs` and `daily_calories`
- Designs:
  - ![Capture Flow](./DESIGNS/capture_flow.png)

## 4. History
- List previous analyses with times and photos
- Designs:
  - ![History](./DESIGNS/history.png)

## 5. Favorites & Recipes
- Proxy via `/v1/app/favorites/*` and `/v1/app/recipes/*`
- Designs:
  - ![Favorites](./DESIGNS/favorites.png)
  - ![Recipes](./DESIGNS/recipes.png)

## 6. Progress + Weight Logs
- Charts: 7/30/90/365
- CRUD `weight_logs`
- Designs:
  - ![Progress Charts](./DESIGNS/progress_charts.png)

## 7. Barcode/Label
- On-device barcode → `/v1/app/label/analyze` stub; OFF later
- Designs:
  - ![Barcode Scan](./DESIGNS/barcode_scan.png)

## 8. Payments
- YooKassa hosted checkout → webhook credits
- Designs:
  - ![Paywall](./DESIGNS/paywall.png)
