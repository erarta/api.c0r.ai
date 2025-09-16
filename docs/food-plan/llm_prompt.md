Food Plan LLM Prompt — Canonical Spec

Important: The LLM call must remain unchanged.

Invocation
- Generator class: FoodPlanGenerator or MealPlanGenerator
- Method: await generate_plan(profile, food_history, days)

Inputs
- profile: user profile dict (age, gender, height_cm, weight_kg, activity_level, goal, dietary_preferences, allergies, daily_calories_target)
- food_history: array of recent logs with kbzhu + metadata
- days: number of days to generate (1–7)

Expected Output
- plan_json: dict keyed by day (e.g., day_1..day_N), each containing meals: breakfast/lunch/dinner/snack with calories/protein/fats/carbs and textual suggestions
- shopping_list_json: aggregated ingredient list across days
- confidence: float (0..1), optional
- model_used: string (provider/model id), optional

Server-side adjustments
- API computes per-day totals regardless of LLM output to ensure consistency.

Quality guidelines
- Respect daily_calories_target if present
- Avoid allergens; honor dietary_preferences
- Prefer simple, accessible ingredients; metric units

Non-breaking rule
- Do not change method signature or returned object keys expected by API.

