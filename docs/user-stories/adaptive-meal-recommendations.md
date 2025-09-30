# 🍽️ User Stories: Adaptive Meal Recommendations

## Feature Overview
AI-powered meal suggestions that dynamically adapt to user preferences, dietary restrictions, cooking skills, time constraints, stress levels, and contextual factors for maximum personalization and adherence.

---

## 📱 Story 1: Preference-Filtered Recommendations

**As a** user with specific dietary restrictions and preferences
**I want** my meal recommendations to automatically exclude foods I can't or won't eat
**So that** every suggestion is actually usable and appealing

### Acceptance Criteria:
- ✅ Hard constraints applied (allergies, dietary restrictions)
- ✅ Soft preferences considered (favorite cuisines, disliked foods)
- ✅ Cooking skill level matched to recipe complexity
- ✅ Time constraints respected in all suggestions
- ✅ Clear reasoning provided for each recommendation

### Example Filtering:
```
User Profile:
🚫 Allergies: Tree nuts, shellfish
🥗 Diet: Pescatarian (no meat, fish OK)
😋 Loves: Italian cuisine, pasta dishes
😖 Avoids: Mushrooms, blue cheese
👩‍🍳 Skills: Intermediate cooking (can handle 30-min recipes)
⏰ Time: Usually has 20-25 minutes for dinner prep

❌ Filtered Out:
• "Chicken Alfredo" (contains meat)
• "Walnut Pesto Pasta" (contains tree nuts)
• "Mushroom Risotto" (contains disliked ingredient)

✅ Recommended:
• "Lemon Garlic Salmon Pasta" (22 min prep)
  - Matches: Italian preference, pescatarian diet, cooking skill
  - Reasoning: "Your favorite Italian flavors with omega-3 rich salmon"

• "Capellini with Cherry Tomatoes" (18 min prep)
  - Matches: Italian cuisine, quick prep, intermediate skill
  - Reasoning: "Simple Italian classic that fits your busy schedule"
```

### Backend Logic:
```python
def _determine_meal_characteristics(
    nutrition_dna: NutritionDNA,
    meal_type: str,
    context: Dict[str, Any],
    enhanced_profile: Dict[str, Any] = None
) -> Dict[str, Any]:

    # Hard constraints (must be respected)
    characteristics['allergies'] = enhanced_profile.get('allergies', [])
    characteristics['dietary_restrictions'] = enhanced_profile.get('dietary_preferences', [])

    # Soft preferences (influence scoring)
    characteristics['preferred_cuisines'] = enhanced_profile.get('preferred_cuisines', [])
    characteristics['avoid_foods'] = enhanced_profile.get('disliked_foods', [])

    # Practical constraints
    if enhanced_profile.get('preference_flags', {}).get('prefers_quick_meals'):
        characteristics['max_prep_time'] = 10
    elif enhanced_profile.get('cooking_time_available') == 'quick':
        characteristics['max_prep_time'] = 15

    return characteristics
```

---

## 📱 Story 2: Context-Aware Suggestions

**As a** user whose eating needs change based on my situation
**I want** meal recommendations that consider my current context
**So that** suggestions fit my immediate circumstances and needs

### Context Factors:

#### 😰 Stress Level Impact
```
High Stress Day Detected 📈

Your Stress Driven profile suggests you might crave:
• Comfort foods for emotional regulation
• Quick prep meals (you're likely short on time)
• Foods rich in magnesium and B-vitamins for stress support

Adapted Recommendations:
🍜 "Creamy Tomato Soup with Grilled Cheese"
   • Comfort food that meets nutritional needs
   • 15-minute prep for busy stress day
   • Includes stress-reducing ingredients

🥗 "Mediterranean Quinoa Bowl"
   • Magnesium-rich quinoa for stress management
   • Familiar flavors reduce decision fatigue
   • Can be prepped in batches for week

🍫 "Dark Chocolate Avocado Mousse"
   • Healthy dessert alternative to stress eating
   • Serotonin boost from dark chocolate
   • Ready in 10 minutes
```

#### 👥 Social Context
```
Cooking for Friends Tonight? 🎉

Your Social Eater profile shows you eat differently in groups:

Shareable Meal Ideas:
🍝 "Build-Your-Own Pasta Bar"
   • Interactive dining experience
   • Accommodates various dietary preferences
   • Impressive but manageable prep

🌮 "Mediterranean Mezze Platter"
   • Perfect for conversation while eating
   • Beautiful presentation for photos
   • Most ingredients can be prepped ahead

💡 Pro Tips for Social Eating:
• Prepare 20% more than calculated portions
• Include 1-2 crowd-pleasing backup options
• Set up self-serve stations to minimize hosting stress
```

#### 🏃 Post-Workout Recovery
```
Post-Workout Nutrition (High Activity Day) 💪

Recommended within 2 hours of exercise:

🥤 "Protein-Packed Berry Smoothie"
   • 25g protein for muscle recovery
   • Simple carbs for glycogen replenishment
   • Anti-inflammatory berries for recovery

🍳 "Quinoa Power Bowl with Eggs"
   • Complete amino acid profile
   • Complex carbs for sustained energy
   • Iron and B-vitamins for energy metabolism

⏰ Timing Recommendations:
• Eat within 30-60 minutes post-workout
• Include both protein and carbohydrates
• Hydrate with 16-24 oz water alongside meal
```

#### 🌧️ Weather Influence
```
Rainy Day Comfort Menu ☔

Weather affects appetite - here are warming options:

🍲 "Hearty Lentil Stew"
   • Warming spices boost mood on gloomy days
   • High fiber keeps you satisfied longer
   • One-pot meal minimizes cleanup

☕ "Spiced Golden Milk Latte"
   • Warming turmeric and ginger
   • Comforting ritual for rainy afternoons
   • Anti-inflammatory benefits

🥧 "Baked Oatmeal with Cinnamon"
   • Fills home with comforting aromas
   • Batch cook for easy week mornings
   • Naturally mood-boosting ingredients
```

---

## 📱 Story 3: Skill-Level Appropriate Recipes

**As a** user with specific cooking abilities and time constraints
**I want** recipes that match my skill level and available time
**So that** I can successfully prepare meals without stress or failure

### Skill Level Adaptations:

#### 👶 Beginner Level (15 min max, minimal technique)
```
Beginner-Friendly Dinner Options:

🍝 "Simple Aglio e Olio"
   ⏰ Prep: 12 minutes
   🔥 Techniques: Boiling pasta, mincing garlic
   🛠️ Tools: Pot, pan, cutting board

   Step-by-step guidance:
   1. Boil water (large pot, high heat)
   2. Add pasta when bubbling vigorously
   3. While pasta cooks: slice garlic (thin slices OK)
   4. Heat oil in pan (medium heat)
   5. Add garlic when oil shimmers
   6. Combine drained pasta with oil mixture

   💡 Beginner Tips:
   • Use timer for pasta cooking
   • Garlic should sizzle gently, not brown
   • Reserve pasta water before draining
   • Taste and adjust salt at the end
```

#### 👨‍🍳 Intermediate Level (30 min max, moderate techniques)
```
Intermediate Challenge:

🐟 "Pan-Seared Salmon with Lemon Butter Sauce"
   ⏰ Prep: 25 minutes
   🔥 Techniques: Pan-searing, sauce making, timing coordination
   🛠️ Tools: Cast iron or heavy pan, whisk, instant-read thermometer

   Skill-building elements:
   • Proper fish searing technique
   • Emulsion sauce (butter into lemon juice)
   • Temperature awareness (fish doneness)
   • Multi-tasking (sauce while fish rests)

   💪 What you'll learn:
   • How to get crispy fish skin
   • Sauce consistency troubleshooting
   • Professional plating techniques
```

#### 👩‍🍳 Advanced Level (45+ min, complex techniques)
```
Advanced Culinary Project:

🥘 "Duck Confit with Cherry Gastrique"
   ⏰ Prep: 3 hours (mostly passive)
   🔥 Techniques: Confit cooking, gastrique, flavor balancing
   🛠️ Tools: Oven-safe pot, candy thermometer, fine-mesh strainer

   Advanced concepts:
   • Low-temperature fat cooking
   • Sweet and sour sauce balancing
   • Proper duck fat temperature control
   • Professional sauce consistency

   🎓 Masterclass elements:
   • Traditional French techniques
   • Temperature precision importance
   • Flavor profile development
   • Restaurant-quality presentation
```

---

## 📱 Story 4: Nutritional Goal Alignment

**As a** user with specific health and fitness goals
**I want** meal recommendations that actively support my objectives
**So that** my diet consistently moves me toward my targets

### Goal-Specific Adaptations:

#### 💪 Weight Loss Focus
```
Weight Loss Optimized Recommendations:

🥗 "High-Volume, Low-Calorie Dinner"
   📊 Stats: 320 calories, feels like 500+

   "Zucchini Noodle Bolognese"
   • Spiralized zucchini replaces pasta (-280 cal)
   • Lean ground turkey instead of beef (-120 cal)
   • Extra vegetables add volume without calories
   • High protein (28g) maintains satiety

   🧠 Psychology: Looks and feels like indulgent pasta dish
   ⚖️ Portion: Large, visually satisfying plate
   🕒 Timing: Earlier dinner supports weight loss

📊 Daily Progress Tracking:
   • Current: 1,240 cal | Target: 1,400 cal
   • Remaining: 160 cal for evening snack
   • Protein: 89g/100g goal ✅
   • Fiber: 28g/25g goal ✅
```

#### 🏋️ Muscle Gain Focus
```
Muscle Building Meal Plan:

🍖 "Post-Workout Protein Power Meal"
   📊 Stats: 650 calories, 45g protein

   "Grilled Chicken & Sweet Potato Stack"
   • 6oz chicken breast (40g protein)
   • Roasted sweet potato (complex carbs for recovery)
   • Avocado (healthy fats for hormone production)
   • Quinoa pilaf (complete amino acid profile)

   ⏰ Optimal Timing:
   • Within 2 hours post-workout
   • Protein synthesis window maximization
   • Carb replenishment for next session

🏗️ Building Phase Tracking:
   • Protein: 45g/180g daily goal
   • Calories: 650/2800 daily goal
   • Leucine: 3.2g (muscle protein synthesis trigger)
   • Post-workout window: ✅ OPTIMAL
```

#### ❤️ Heart Health Focus
```
Cardiovascular Health Menu:

🐟 "Omega-3 Rich Mediterranean Dinner"
   📊 Stats: 420 calories, 2.1g omega-3 fatty acids

   "Baked Cod with Olive Tapenade"
   • Wild-caught cod (lean protein, low mercury)
   • Olive tapenade (monounsaturated fats)
   • Roasted vegetables (antioxidants, fiber)
   • Whole grain couscous (complex carbs)

   ❤️ Heart Benefits:
   • Omega-3s reduce inflammation
   • Fiber supports cholesterol management
   • Potassium helps regulate blood pressure
   • Antioxidants protect arterial health

📈 Heart Health Metrics:
   • Omega-3: 2.1g/2.0g daily goal ✅
   • Fiber: 12g contributes to 35g goal
   • Sodium: 340mg (well under limit)
   • Saturated fat: 2.1g (minimal)
```

---

## 📱 Story 5: Real-Time Adaptation

**As a** user whose circumstances change throughout the day
**I want** meal recommendations that can adjust to unexpected situations
**So that** I always have viable options regardless of what happens

### Adaptive Scenarios:

#### 🚨 Emergency Quick Meal (15 minutes or less)
```
Quick Change of Plans! ⚡

Original plan: "Herb-Crusted Salmon" (45 min prep)
New situation: Unexpected meeting in 20 minutes

Adapted Recommendation:
🥙 "Mediterranean Wrap & Soup"
   ⏰ Prep: 8 minutes
   🍽️ Same flavors: Mediterranean herbs and vegetables
   📊 Similar nutrition: 380 cal vs 390 cal planned

   Quick Assembly:
   • Whole wheat tortilla + hummus
   • Pre-washed greens + cherry tomatoes
   • Crumbled feta + cucumber
   • Microwave soup cup (low-sodium)

   🔄 Plan Update: Salmon moved to tomorrow's dinner
   📝 Shopping list automatically adjusted
```

#### 🛒 Missing Ingredients Substitution
```
Ingredient Swap Required! 🔄

Planned: "Thai Basil Stir Fry"
Missing: Fresh basil (store was out)

AI Suggestion:
🌶️ "Thai Mint Stir Fry" (substitute available)
   • Fresh mint provides similar aromatic profile
   • Slightly sweeter, less peppery than basil
   • All other ingredients remain the same

Alternative Options:
🍃 "Thai Cilantro Stir Fry" (if mint unavailable)
🌿 "Thai Herb Blend Stir Fry" (dried herbs)

💡 Learning Note: System remembers your local store's typical stock patterns for future planning
```

#### 👥 Unexpected Guests
```
Surprise Dinner Guests! 🎉

Original plan: Individual salmon fillets (serves 2)
New need: Feed 5 people

Scaled Recommendation:
🍝 "Family-Style Salmon Pasta"
   📊 Same ingredients, different preparation:
   • Flake salmon into pasta sauce
   • Stretch with additional pasta and vegetables
   • Add extra seasonings for crowd appeal

   🛒 Quick additions needed:
   • 1 lb pasta (instead of 0.5 lb)
   • Extra vegetables for volume
   • Parmesan for topping

   ⏰ Prep time: 25 min (only 5 min longer)
   💰 Cost per serving: Actually decreases!
```

---

## 📱 Story 6: Learning from Feedback

**As a** user who provides feedback on meal recommendations
**I want** the system to learn from my preferences and improve over time
**So that** suggestions become more accurate and appealing

### Feedback Integration:

#### ⭐ Rating System
```
Rate Your Meal: "Lemon Herb Chicken"

How was this meal? ⭐⭐⭐⭐⭐ (4/5 stars)

Quick feedback (optional):
☑️ Delicious flavor
☑️ Perfect portion size
☐ Too much prep time
☑️ Will make again
☐ Too salty
☐ Not filling enough

🤖 AI Learning:
• Lemon herb flavor combination: Loved ✅
• Chicken breast preparation method: Approved ✅
• 25-minute prep time: Acceptable ✅
• Italian herbs: Added to preferred seasonings ✅

Future Impact:
• More lemon-herb combinations in recommendations
• Similar chicken preparation techniques prioritized
• Italian seasoning blend suggested for other proteins
```

#### 📝 Detailed Feedback Processing
```
Feedback: "Loved the flavor but took way longer than 20 minutes - more like 35!"

AI Analysis & Adjustments:
🕒 Recipe Timing Update:
   • "Honey Garlic Salmon" prep time: 20 min → 25 min
   • Added note: "Allow extra 5-10 min for first-time preparation"
   • Beginner timing vs experienced cook differentiation

📚 User Profile Update:
   • Cooking speed: Adjusted to 80% of recipe estimates
   • Future recommendations: Add 20% buffer to all prep times
   • Skill level: Confirmed as "developing intermediate"

🎯 Future Recommendations:
   • Recipes now filtered with realistic timing for your speed
   • More detailed prep instruction provided
   • "Quick win" recipes prioritized for busy days
```

#### 🔄 Preference Evolution Tracking
```
Preference Learning Over Time:

Month 1: "I don't like spicy food" (heat tolerance: 1/10)
   • Recommendations avoided all spices
   • Focused on mild, familiar flavors

Month 2: Rated "Mild Curry" 4/5 stars
   • System notes: Tolerance for mild warm spices
   • Heat tolerance updated: 1/10 → 3/10

Month 3: Requested "something with more flavor"
   • AI suggests: Medium spice dishes
   • User tries and rates highly

Month 6: Regular enjoyment of moderately spicy dishes
   • Heat tolerance: 6/10
   • Regularly requests bold flavors
   • System learned: User preferences can evolve significantly

💡 AI Insight: "Your spice tolerance has grown! You might enjoy these previously 'too spicy' dishes now."
```

---

## 🔧 Technical Implementation

### Recommendation Engine:
```python
class AdaptiveMealRecommender:
    @classmethod
    def recommend_meal(
        cls,
        nutrition_dna: NutritionDNA,
        meal_type: str,
        context: Dict[str, Any] = None,
        constraints: Dict[str, Any] = None,
        enhanced_profile: Dict[str, Any] = None
    ) -> PersonalizedMealRecommendation:

        # Step 1: Determine meal characteristics
        characteristics = cls._determine_meal_characteristics(
            nutrition_dna, meal_type, context, enhanced_profile
        )

        # Step 2: Apply hard constraints (allergies, restrictions)
        available_meals = cls._filter_by_constraints(characteristics)

        # Step 3: Score by preferences and context
        scored_meals = cls._score_by_preferences(
            available_meals, characteristics, enhanced_profile
        )

        # Step 4: Select best match
        selected_meal = cls._select_optimal_meal(scored_meals)

        # Step 5: Generate reasoning
        reasoning = cls._generate_meal_reasoning(
            nutrition_dna, selected_meal, context, characteristics
        )

        return PersonalizedMealRecommendation(
            dish_name=selected_meal['name'],
            reasoning=reasoning,
            matches_energy_level=characteristics.get('energy_match', False),
            addresses_typical_craving=characteristics.get('craving_match', False),
            fits_schedule_pattern=characteristics.get('schedule_match', True),
            supports_current_goal=characteristics.get('goal_match', True),
            # ... nutrition and preparation details
        )
```

### Database Schema:
```sql
CREATE TABLE meal_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    nutrition_dna_id UUID REFERENCES nutrition_dna(id),

    -- Meal details
    meal_type TEXT NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    dish_name TEXT NOT NULL,
    reasoning TEXT,

    -- Personalization scores
    matches_energy_level BOOLEAN DEFAULT FALSE,
    addresses_typical_craving BOOLEAN DEFAULT FALSE,
    fits_schedule_pattern BOOLEAN DEFAULT FALSE,
    supports_current_goal BOOLEAN DEFAULT FALSE,

    -- Context data
    context_data JSONB DEFAULT '{}',
    recommendation_score DECIMAL(3,2) DEFAULT 0.5,

    -- Feedback tracking
    user_feedback INTEGER CHECK (user_feedback >= 1 AND user_feedback <= 5),
    feedback_notes TEXT,
    used_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 📊 Success Metrics

- **Recommendation Acceptance Rate:** 78% (target: >75%)
- **User Rating Average:** 4.2/5.0 stars (target: >4.0)
- **Feedback Integration Speed:** <24 hours for preference updates
- **Context Adaptation Accuracy:** 85% appropriate for situation
- **Constraint Compliance:** 99.8% (zero tolerance for allergy violations)
- **Recipe Success Rate:** 92% of users successfully complete recommended recipes
- **Preference Evolution Detection:** 89% accuracy in identifying taste changes