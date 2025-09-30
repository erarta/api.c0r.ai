Supabase Client for Food Plan

Scope
- Centralize DB ops for food plans in common/db/supabase_service.py
- Provide a stable API for routers to fetch context, check unlock status, and upsert/fetch plans.

Module: common/db/supabase_service.py
- get_meal_plan_context(user_id): returns profile, food_history (30d), history_summary
- check_meal_plan_unlock_status(user_id, bypass_subscription): computes unlocked flag from last 14d
- upsert_meal_plan(user_id, plan_record, force): insert/update by (user_id, start_date, end_date)
- get_meal_plan_covering_date(user_id, day)
- get_latest_meal_plan(user_id)

Dependencies
- common/db/client.py → supabase
- migrations/database/2025-08-08_features_favorites_plans_recipes.sql → meal_plans

Environment
- SUPABASE_URL, SUPABASE_SERVICE_KEY (required)

Notes
- Function bodies handle missing Supabase by returning safe defaults for dev.

