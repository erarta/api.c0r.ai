Food Plan Feature — Architecture and Integration Guide

This document summarizes how the Food Plan feature works end-to-end so it can be restored on the main branch with minimal friction. The LLM call remains unchanged — only the service boundaries and DB interactions are documented here.

Goals
- Generate a day-by-day food plan for a user using an LLM with user context (profile + history).
- Persist plans in Supabase (meal_plans table) with a unique constraint on (user_id, start_date, end_date).
- Expose public and internal endpoints to generate and fetch current plans.
- Cache heavy context (history summary) for faster re-use.

High-level flow
1. Client calls API POST /food-plan/generate (or the internal variant).
2. API builds context via supabase_service.get_meal_plan_context(user_id).
3. API checks unlock status via supabase_service.check_meal_plan_unlock_status(...) and feature flags.
4. API calls the LLM generator (unchanged) to produce a plan.
5. API computes per-day totals server-side for safety.
6. API persists plan via supabase_service.upsert_meal_plan(...).
7. API returns the plan; subsequent reads use get_*meal_plan* helpers.

Key components
- API router: services/api/public/routers/meal_plan.py
- Supabase service: common/db/supabase_service.py
- Caching helpers: common/cache/redis_client.py (dummy in dev)
- Feature flags: common/config/feature_flags.py (BYPASS_SUBSCRIPTION)
- Auth deps (dev shim): deps.py (provides AuthContext, require_auth_context)
- Migration (tables): migrations/database/2025-08-08_features_favorites_plans_recipes.sql

Database schema
meal_plans is created in the migration above (Meal plans section).

Columns (essential):
- id uuid PK, user_id uuid, start_date date, end_date date
- plan_json jsonb, shopping_list_json jsonb, generated_from text
- Unique index on (user_id, start_date, end_date)

Endpoints (detailed in routes.md)
- POST /food-plan/generate
- POST /food-plan/generate-internal
- GET /food-plan/current
- GET /food-plan/current-internal
- GET /food-plan/unlock-status-internal

LLM integration (unchanged)
- The generator class is imported as FoodPlanGenerator or MealPlanGenerator and invoked as:
  - await generator.generate_plan(profile, food_history, days)
- Output must include plan_json, shopping_list_json, with optional confidence, model_used.
- See llm_prompt.md for the canonical prompt structure and JSON schema expectations.

Configuration
Required env:
- SUPABASE_URL, SUPABASE_SERVICE_KEY
- INTERNAL_API_TOKEN (for internal endpoints)
Optional:
- BYPASS_SUBSCRIPTION=true to skip unlock checks in dev

Caching
- Redis use is optional; common/cache/redis_client.py provides a dummy async client for dev.
- Cache key helper: make_cache_key(namespace, params)

Security
- Internal endpoints require X-Internal-Token: $INTERNAL_API_TOKEN.
- Public endpoints require an AuthContext (dev shim accepts X-User-ID). Replace with real auth in production.

Porting checklist
- Ensure env vars above are set for main.
- Restore or include common/db/supabase_service.py.
- Keep the LLM generator code unchanged; only wire the router and service.
- Verify DB migration for meal_plans exists in main or apply it.
- Run curl smoke tests (see routes.md).

