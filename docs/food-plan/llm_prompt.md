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
- intro_summary: short human-like summary (2–3 sentences) about last ~2 weeks eating patterns and that the plan accounts for profile (goal, preferences, allergies)
- plan_json: dict keyed by day (e.g., day_1..day_N), each containing meals: breakfast/lunch/dinner with calories/protein/fats/carbs and human-like textual suggestions
- shopping_list_json: aggregated ingredient list across days
- confidence: float (0..1), optional
- model_used: string (provider/model id), optional

Server-side adjustments
- API computes per-day totals regardless of LLM output to ensure consistency.

Quality guidelines
- Respect daily_calories_target if present
- Avoid allergens; honor dietary_preferences
- Prefer simple, accessible ingredients; metric units
- Diversify meals across days: avoid repeating the same dish; rotate protein sources (chicken, turkey, fish, eggs, legumes, seafood); vary sides (rice, quinoa, buckwheat, potatoes, veggies)
- Flexible calories: keep daily total around target but vary ±150–200 kcal to look natural
- Human-like dish descriptions: explain why the dish is chosen and how it helps the day
- Format top-down per day: Day → Breakfast → Lunch → Dinner → Daily totals; separate days with ---

Non-breaking rule
- Do not change method signature or returned object keys expected by API.

