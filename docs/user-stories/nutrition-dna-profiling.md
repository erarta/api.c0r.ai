# 🧬 User Stories: Nutrition DNA Profiling

## Feature Overview
AI-powered personality profiling that analyzes user behavior patterns to assign one of 8 eating personality archetypes, enabling deeply personalized nutrition recommendations.

---

## 📱 Story 1: DNA Profile Generation

**As a** user who has completed nutrition onboarding
**I want** my eating personality to be automatically analyzed
**So that** I receive recommendations tailored to my behavioral patterns

### Acceptance Criteria:
- ✅ DNA generated automatically after sufficient data collection
- ✅ Confidence score indicates reliability (minimum 60%)
- ✅ Clear explanation of assigned archetype
- ✅ Specific behavioral insights provided
- ✅ Recommendations adapted to archetype characteristics

### DNA Generation Flow:
```
🧠 Analyzing your nutrition patterns...

Data Sources:
✅ Questionnaire responses (25+ data points)
✅ Food analysis history (12+ logs)
✅ Meal timing patterns (2+ weeks)
✅ Preference behaviors (selections & feedback)

🧬 DNA Analysis Complete!

Your Eating Personality: STRESS DRIVEN (84% confidence)

Key Traits:
• Food choices influenced by emotional state
• Higher calorie intake during stressful periods
• Prefers comfort foods when overwhelmed
• Benefits from structured eating schedules
• Responds well to stress-management techniques
```

### Backend Processing:
```python
# Automatic DNA generation after onboarding
nutrition_dna = NutritionDNAGenerator.generate_nutrition_dna(
    profile=enhanced_user_profile,
    food_history=user_food_logs,
    context_data=behavioral_patterns
)

# DNA includes:
# - archetype: EatingPersonality enum
# - confidence_score: 0.6-1.0
# - energy_patterns: morning/evening preferences
# - temporal_patterns: meal timing flexibility
# - social_patterns: eating alone vs with others
# - psychological_patterns: stress/emotional triggers
```

---

## 📱 Story 2: Archetype Explanation & Insights

**As a** user with a newly assigned eating personality
**I want** to understand what my archetype means
**So that** I can see how it applies to my meal recommendations

### The 8 Nutrition DNA Archetypes:

#### 🌅 Early Bird Planner
**Characteristics:**
- Peak energy and appetite in morning hours
- Prefers to plan meals in advance
- Structured eating schedule works best
- Often skips dinner or eats lightly in evening

**Personalization:**
- Larger, more complex breakfasts
- Simple, light dinner options
- Meal prep suggestions for advance planning
- Morning-focused grocery shopping tips

**User Message:**
```
🌅 You're an Early Bird Planner!

Your Strengths:
• Natural morning energy for healthy choices
• Great at meal prep and advance planning
• Consistent breakfast habits build strong foundations

Your Growth Areas:
• Evening meals might be rushed or skipped
• May need reminders for balanced dinners
• Weekend schedule disruptions affect patterns

🎯 Your Plans Will Include:
• Hearty, nutritious breakfast options (400-500 cal)
• Light, easy dinner recipes (300-400 cal)
• Weekend meal prep suggestions
• Morning energy optimization tips
```

#### 😰 Stress Driven
**Characteristics:**
- Food choices strongly influenced by emotional state
- Higher calorie intake during stressful periods
- Gravitates toward comfort foods when overwhelmed
- Benefits from structured eating to manage triggers

**Personalization:**
- Healthy comfort food alternatives
- Stress-reduction meal timing
- Emergency snack suggestions
- Mindful eating techniques integration

#### 👥 Social Eater
**Characteristics:**
- Eating patterns heavily influenced by social environment
- Different food choices when alone vs with others
- Restaurant and gathering food decisions challenging
- Enjoys cooking for and eating with friends/family

#### 💼 Busy Professional
**Characteristics:**
- Limited time for meal preparation
- Convenience often trumps optimal nutrition
- Irregular eating schedules due to work demands
- Prefers grab-and-go options

#### 🏃 Weekend Warrior
**Characteristics:**
- Stark contrast between weekday and weekend eating
- Disciplined during work week, relaxed on weekends
- Balances active lifestyle with social eating
- Plans around workout and activity schedules

#### 🌿 Intuitive Grazer
**Characteristics:**
- Prefers smaller, frequent meals throughout day
- Strong connection to hunger and satiety cues
- Flexible eating times based on body signals
- Dislikes rigid meal schedules

#### 😴 Late Starter Impulsive
**Characteristics:**
- Peak appetite and energy in afternoon/evening
- Often skips breakfast or eats very lightly
- Spontaneous food decisions and meal timing
- Creative with food combinations and recipes

#### ⚖️ Structured Balanced
**Characteristics:**
- Consistent eating patterns across all days
- Balanced approach to all food groups
- Moderate portions and steady energy levels
- Rarely experiences extreme cravings or restrictions

---

## 📱 Story 3: DNA-Based Plan Customization

**As a** user with a specific eating personality
**I want** my meal plans to reflect my archetype characteristics
**So that** following the plan feels natural and sustainable

### Archetype-Specific Customizations:

#### For Stress Driven Users:
```
🧠 Your Stress Driven plan includes:

Comfort Food Makeovers:
• Greek yogurt parfait instead of ice cream
• Baked sweet potato fries vs regular fries
• Dark chocolate (70%+) for chocolate cravings
• Herbal teas for emotional regulation

Stress Prevention Strategies:
• Protein-rich snacks to stabilize mood
• Magnesium-rich foods for relaxation
• Scheduled eating times to prevent stress-skipping
• Weekend stress-baking healthy alternatives

Emergency Kit Suggestions:
• Pre-portioned nuts for stress snacking
• Frozen berries for instant "dessert"
• Herbal tea variety pack for emotional moments
```

#### For Busy Professional Users:
```
💼 Your Busy Professional plan focuses on:

Quick Wins (Under 10 minutes):
• Overnight oats with protein powder
• Pre-made salad jars (grab and go)
• Sheet pan meals (prep Sunday, eat all week)
• Protein smoothie packs (just add liquid)

Office-Friendly Options:
• Desk-suitable snacks (no heating required)
• One-handed eating foods for meetings
• Travel-friendly containers recommended
• Backup meal suggestions for late nights

Efficiency Tips:
• Sunday meal prep in 2 hours
• Grocery delivery optimization
• Kitchen tools that save time
• Batch cooking strategies
```

---

## 📱 Story 4: DNA Evolution & Updates

**As a** long-term user whose eating patterns evolve
**I want** my nutrition DNA to update based on new behaviors
**So that** my recommendations stay accurate over time

### Acceptance Criteria:
- ✅ DNA recalculated monthly with new data
- ✅ Confidence score adjusted based on pattern consistency
- ✅ Archetype changes communicated clearly
- ✅ Historical DNA tracking for progress awareness
- ✅ Sudden changes flagged for user confirmation

### DNA Update Notification:
```
🧬 Your Nutrition DNA has evolved!

Previous: Stress Driven (78% confidence)
Current: Structured Balanced (82% confidence)

What Changed:
📈 More consistent eating times (+40%)
📈 Reduced stress-eating incidents (-60%)
📈 Better weekend/weekday balance (+25%)
📈 Increased meal planning frequency (+50%)

🎉 Congratulations on your positive changes!

Your new meal plans will reflect:
• More variety in cuisine types
• Balanced macro distribution
• Flexible portion sizes
• Seasonal ingredient rotation

[View Updated Recommendations] [See DNA History]
```

### DNA History View:
```
🧬 Your Nutrition DNA Journey

Sep 2025: Structured Balanced (82%) ← Current
Aug 2025: Stress Driven → Structured Balanced (transition)
Jul 2025: Stress Driven (78%)
Jun 2025: Stress Driven (84%)
May 2025: Social Eater → Stress Driven (major life change)
Apr 2025: Social Eater (91%) ← Started with high confidence

🏆 Growth Achievements:
• Reduced stress eating by 60%
• Improved meal timing consistency by 40%
• Maintained balanced weekend eating for 2+ months
```

---

## 📱 Story 5: Confidence Score & Reliability

**As a** user receiving DNA-based recommendations
**I want** to understand how reliable my personality profile is
**So that** I can trust the personalization level

### Confidence Score Ranges:

#### 🟢 High Confidence (80-100%)
```
🧬 Stress Driven (91% confidence)

Your profile is highly reliable:
✅ Consistent patterns across 3+ months
✅ Strong correlation between triggers and responses
✅ Clear preference clusters identified
✅ Behavioral predictions highly accurate

Personalization Level: MAXIMUM
Your recommendations use advanced behavioral modeling.
```

#### 🟡 Good Confidence (65-79%)
```
🧬 Weekend Warrior (72% confidence)

Your profile is well-established:
✅ Clear weekday vs weekend patterns
⚠️ Some inconsistencies in stress responses
✅ Strong activity-food correlations
⚠️ Limited social eating data

Personalization Level: HIGH
Your recommendations focus on well-established patterns.
```

#### 🟠 Moderate Confidence (60-64%)
```
🧬 Early Bird Planner (63% confidence)

Your profile is developing:
✅ Clear morning energy patterns
⚠️ Evening eating data limited
⚠️ Weekend patterns still emerging
⚠️ Need more meal prep feedback

Personalization Level: MODERATE
Your recommendations use basic patterns with conservative assumptions.
```

#### 🔴 Low Confidence (<60%)
```
🧬 Profile Developing (45% confidence)

We need more data to personalize accurately:
⚠️ Inconsistent meal timing patterns
⚠️ Limited stress-eating correlation data
⚠️ Mixed preference signals
⚠️ Need 2-3 more weeks of food logs

Personalization Level: BASIC
Your recommendations use general healthy eating principles.

💡 Log 5+ meals this week to improve your profile accuracy!
```

---

## 📱 Story 6: DNA Sharing & Social Features

**As a** user proud of my nutrition progress
**I want** to share my eating personality insights
**So that** I can inspire others and find similar nutrition journeys

### Shareable Insights:
```
🧬 Share Your Nutrition DNA

[📱 Share to Social Media]
"Just discovered I'm a Stress Driven eater! 😰➡️⚖️ Working on becoming more Structured Balanced with @c0r_ai's personalized meal plans. My stress eating is down 60% in 2 months! 💪 #NutritionDNA #HealthJourney"

[📊 Generate Progress Image]
Visual showing:
• DNA archetype with icon
• Key improvements over time
• Confidence score evolution
• Major achievements unlocked

[👥 Find Similar Profiles]
Connect with other users who share your archetype for:
• Recipe exchanges
• Challenge participation
• Motivation and support
• Success story sharing
```

---

## 🔧 Technical Implementation

### DNA Generation Algorithm:
```python
class NutritionDNAGenerator:
    @classmethod
    def generate_nutrition_dna(
        cls,
        profile: Dict[str, Any],
        food_history: List[Dict[str, Any]],
        context_data: Optional[List[Dict[str, Any]]] = None
    ) -> NutritionDNA:
        # Analyze temporal patterns
        temporal_analysis = cls._analyze_temporal_patterns(food_history)

        # Analyze psychological patterns
        psychological_analysis = cls._analyze_psychological_patterns(profile, food_history)

        # Analyze social patterns
        social_analysis = cls._analyze_social_patterns(context_data or [])

        # Determine archetype
        archetype = cls._determine_archetype(
            temporal_analysis, psychological_analysis, social_analysis
        )

        # Calculate confidence
        confidence = cls._calculate_confidence_score(
            temporal_analysis, psychological_analysis, social_analysis
        )

        return NutritionDNA(
            archetype=archetype,
            confidence_score=confidence,
            energy_patterns=temporal_analysis['energy'],
            temporal_patterns=temporal_analysis['timing'],
            social_patterns=social_analysis,
            psychological_patterns=psychological_analysis,
            optimization_zones=cls._identify_optimization_zones(profile, food_history)
        )
```

### Database Schema:
```sql
CREATE TABLE nutrition_dna (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    archetype TEXT NOT NULL CHECK (archetype IN (
        'EARLY_BIRD_PLANNER', 'STRESS_DRIVEN', 'SOCIAL_EATER',
        'BUSY_PROFESSIONAL', 'WEEKEND_WARRIOR', 'INTUITIVE_GRAZER',
        'LATE_STARTER_IMPULSIVE', 'STRUCTURED_BALANCED'
    )),
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    -- Pattern data stored as JSONB for flexibility
    energy_patterns JSONB DEFAULT '{}',
    temporal_patterns JSONB DEFAULT '{}',
    social_patterns JSONB DEFAULT '{}',
    psychological_patterns JSONB DEFAULT '{}',
    optimization_zones JSONB DEFAULT '[]',
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 📊 Success Metrics

- **DNA Generation Success Rate:** 95% (minimum 60% confidence)
- **Archetype Accuracy:** 85% user agreement with assigned personality
- **Confidence Score Improvement:** Average +15% over 3 months
- **Plan Satisfaction Correlation:** 0.82 between confidence score and user ratings
- **Behavioral Prediction Accuracy:** 78% for high-confidence profiles
- **Archetype Stability:** 89% of users maintain same archetype for 3+ months