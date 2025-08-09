# Phase 1 — Migrations (Tracker MVP)

This summarizes DB changes required for Phase 1 (no social). Keep changes minimal; reuse existing tables.

## Prerequisites (ensure applied)
- 2025-08-05_daily_calories_table.sql — creates `daily_calories` + indexes + RLS
- 2025-08-08_features_favorites_plans_recipes.sql — favorites/recipes tables

## New (Phase 1)

### 1) Optional: link Supabase users to app accounts
Add `auth_user_id` to `users` for app identity mapping (Supabase JWT → users.id). Bot continues to use `telegram_id`.

```sql
-- Users: add Supabase auth mapping
ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_user_id uuid UNIQUE;
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
COMMENT ON COLUMN users.auth_user_id IS 'Supabase auth.user_id mapped to app user';
```

Usage:
- App: resolve `users.id` by `auth_user_id = auth.uid()` (create on first login if missing)
- Bot: resolve by `telegram_id` (existing)

### 2) Weight logs for progress charts
Add a simple table for user weight history with RLS.

```sql
-- Weight logs
CREATE TABLE IF NOT EXISTS weight_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  date date NOT NULL,
  weight_kg numeric(5,2) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (user_id, date)
);
CREATE INDEX IF NOT EXISTS idx_weight_logs_user_date ON weight_logs(user_id, date);

-- RLS
ALTER TABLE weight_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY IF NOT EXISTS weight_logs_select_self ON weight_logs
  FOR SELECT USING (user_id::text = auth.uid()::text);
CREATE POLICY IF NOT EXISTS weight_logs_insert_self ON weight_logs
  FOR INSERT WITH CHECK (user_id::text = auth.uid()::text);
CREATE POLICY IF NOT EXISTS weight_logs_update_self ON weight_logs
  FOR UPDATE USING (user_id::text = auth.uid()::text);
CREATE POLICY IF NOT EXISTS weight_logs_delete_self ON weight_logs
  FOR DELETE USING (user_id::text = auth.uid()::text);

COMMENT ON TABLE weight_logs IS 'User weight entries for progress tracking';
```

Note: If your app always hits your API (and not Supabase PostgREST directly), RLS policies are optional but recommended for safety.

## No changes in Phase 1
- Social tables (`food_posts`, `followers`, `post_likes`, `post_comments`, `conversations`, `messages`) — Phase 2 only
- Payments schema — reuse existing; YooKassa webhook already updates credits
- Label/barcode — no schema changes (stub endpoint only)

## Rollback notes
- To drop `auth_user_id` safely, ensure no app users rely on it; then `ALTER TABLE users DROP COLUMN auth_user_id;`
- To drop `weight_logs`: `DROP TABLE IF EXISTS weight_logs CASCADE;`
