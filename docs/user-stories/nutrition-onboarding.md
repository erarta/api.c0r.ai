# 🎯 User Stories: Nutrition Onboarding

## Feature Overview
Personalized nutrition questionnaire that collects user preferences when they first create a meal plan, ensuring maximum personalization from day one.

---

## 📱 Story 1: First-Time Food Plan Request

**As a** new user who wants to create their first meal plan
**I want** to complete a personalized nutrition questionnaire
**So that** my meal plans are tailored to my specific needs and preferences

### Acceptance Criteria:
- ✅ System detects user has not completed onboarding
- ✅ User sees onboarding prompt instead of immediate plan generation
- ✅ Choice between Quick Setup (2 min) and Full Personalization (7 min)
- ✅ Questionnaire covers all essential preference categories
- ✅ Progress tracking shows completion percentage
- ✅ User can save partial progress and return later

### UI Flow:
```
1. User clicks: "🍽️ Create Food Plan"
2. System message: "⚡ Let's create your perfect nutrition plan!"
3. Two options appear:
   - "🚀 Quick Setup (2 min)" - 5 essential questions
   - "🎯 Full Personalization (7 min)" - Complete questionnaire
   - "⏸️ Skip for now" - Basic plan with future setup reminder
```

### Backend Flow:
```
1. Bot handler checks: check_user_onboarding_status(user_id)
2. If has_profile = false → redirect to onboarding
3. Start questionnaire flow via start_nutrition_onboarding()
4. Track responses in nutrition_questionnaire_responses table
5. Generate NutritionPreferences object and save to user_profiles
```

---

## 📱 Story 2: Quick Setup Flow

**As a** busy user who wants meal plans quickly
**I want** to complete a shortened questionnaire
**So that** I get personalized plans without spending too much time

### Acceptance Criteria:
- ✅ Questionnaire limited to 5 most impactful questions
- ✅ Each question has clear, intuitive options
- ✅ Completion time under 2 minutes
- ✅ Results provide good baseline personalization
- ✅ Option to upgrade to full questionnaire later

### Questions Asked:
1. **Primary Goal:** 💪 Weight Loss | ⚖️ Maintenance | 🏋️ Muscle Gain
2. **Dietary Restrictions:** 🥗 Vegetarian | 🚫 Allergies | ✅ No Restrictions
3. **Cooking Time:** ⚡ Under 15 min | 👨‍🍳 15-30 min | 🍽️ Love Cooking
4. **Activity Level:** 🛋️ Low | 🚶 Moderate | 🏃 High
5. **Cuisine Preference:** 🍝 European | 🍜 Asian | 🌮 Variety

### UI Elements:
```
Progress bar: ████████░░ 80% Complete
Current question: 4/5

"What's your cooking time preference?"

[⚡ Under 15 minutes - Quick meals for busy days]
[👨‍🍳 15-30 minutes - Moderate prep time]
[🍽️ Love cooking - Complex recipes welcome]

[⬅️ Back] [Next ➡️]
```

---

## 📱 Story 3: Full Personalization Flow

**As a** user who wants maximum meal plan customization
**I want** to complete a comprehensive nutrition questionnaire
**So that** my plans consider all my preferences, restrictions, and lifestyle factors

### Acceptance Criteria:
- ✅ WebApp interface for complex multi-choice questions
- ✅ 7 category sections with logical flow
- ✅ Adaptive questions based on previous answers
- ✅ Save progress between sections
- ✅ Rich personalization data for meal generation

### Categories & Questions:

#### 1. 🎯 Goals & Motivation (3 questions)
- Primary nutrition goal
- Target timeline
- Main motivation factors

#### 2. 🚫 Restrictions & Allergies (4 questions)
- Food allergies (multi-select)
- Dietary restrictions (vegetarian, keto, etc.)
- Foods to avoid
- Sensitivity levels

#### 3. 😋 Taste Preferences (5 questions)
- Favorite cuisines (multi-select)
- Preferred proteins
- Favorite vegetables/grains
- Disliked foods
- Spice tolerance

#### 4. ⏰ Eating Patterns (4 questions)
- Meal timing preferences
- Eating frequency (3 meals vs 6 small meals)
- Snacking habits
- Weekend eating style

#### 5. 👩‍🍳 Lifestyle & Cooking (3 questions)
- Cooking skill level
- Available cooking time
- Meal prep willingness

#### 6. 🏃‍♀️ Health & Activity (4 questions)
- Activity level details
- Health conditions
- Supplement usage
- Water intake goals

#### 7. 👥 Social Habits (2 questions)
- Social eating frequency
- Cooking for others frequency

### WebApp Flow:
```
Section Header: 🎯 Goals & Motivation (1/7)
Progress: ██░░░░░░░░ 14%

Question 1/3: What's your primary nutrition goal?
○ Lose weight (10-50+ lbs)
○ Maintain current weight and improve health
○ Gain muscle mass
○ Manage specific health condition
○ Improve energy and mood
○ Other: [text input]

[Continue →]
```

---

## 📱 Story 4: Onboarding Completion

**As a** user who has completed the nutrition questionnaire
**I want** to see a summary of my profile and receive my first personalized plan
**So that** I understand how my preferences influence my recommendations

### Acceptance Criteria:
- ✅ Personalized summary showing detected eating personality
- ✅ Key preferences highlighted
- ✅ First meal plan generated immediately
- ✅ Introduction to personalization features
- ✅ Options to modify preferences later

### Completion Flow:
```
✅ Questionnaire Complete!

🧬 Your Nutrition DNA: Early Bird Planner (88% confidence)
You prefer structured mornings and plan meals in advance.

📋 Your Profile:
🎯 Goal: Weight loss (1-2 lbs/week)
🚫 Avoiding: Gluten, high-sodium foods
😋 Loves: Mediterranean cuisine, lean proteins
⏰ Eating: 3 meals + 1 snack, breakfast at 7:30 AM
👩‍🍳 Cooking: Intermediate skills, 20-30 min available

[📋 View My First Plan] [⚙️ Adjust Settings]
```

### Personalized First Plan:
```
✅ Your personalized 3-day plan is ready!

🧠 Generated using your Early Bird Planner profile:
• Mediterranean-focused recipes matching your taste preferences
• Gluten-free options for your dietary needs
• 20-30 minute prep times fitting your schedule
• High-protein meals supporting weight loss goal
• Structured meal times aligned with your morning energy

📅 Plan Period: Sep 25-27, 2025
⚡ 1,650 kcal daily average (supporting 1-2 lb/week loss)

[View Full Plan 📋] [Shopping List 🛒] [Modify Preferences ⚙️]
```

---

## 📱 Story 5: Preference Updates

**As a** user with changing dietary needs
**I want** to easily update my nutrition preferences
**So that** my future meal plans remain relevant and useful

### Acceptance Criteria:
- ✅ Easy access to preference editing from main menu
- ✅ Category-based editing (don't need to redo everything)
- ✅ Preview how changes affect future recommendations
- ✅ Instant application to next plan generation
- ✅ Change history for rollback if needed

### Settings Menu:
```
⚙️ Nutrition Preferences

🎯 Goals & Timeline
   Current: Weight loss, 3-month plan
   [Edit Goals →]

🚫 Restrictions & Allergies
   Current: Gluten-free, No nuts
   [Edit Restrictions →]

😋 Taste Preferences
   Current: Mediterranean, Asian cuisines
   [Edit Tastes →]

⏰ Eating Patterns
   Current: 3 meals + snack, early breakfast
   [Edit Patterns →]

👩‍🍳 Cooking & Lifestyle
   Current: Intermediate, 20-30 min prep
   [Edit Cooking →]

🏃‍♀️ Health & Activity
   Current: Moderate activity, no conditions
   [Edit Health →]

[🔄 Retake Full Questionnaire]
[📊 View My Nutrition DNA]
```

### Edit Example:
```
🚫 Editing Restrictions & Allergies

Current Allergies: Nuts, Gluten
☑️ Tree nuts (almonds, walnuts, etc.)
☐ Peanuts
☑️ Gluten (wheat, barley, rye)
☐ Dairy products
☐ Shellfish
☐ Eggs
☐ Soy products

[+ Add Other Allergy]

✅ Save Changes    🚫 Cancel

💡 Tip: Changes apply to all future meal plans
```

---

## 📱 Story 6: Skipped Onboarding Reminder

**As a** user who skipped initial onboarding
**I want** to be reminded to complete my profile
**So that** I can improve my meal plan personalization when ready

### Acceptance Criteria:
- ✅ Non-intrusive reminders after basic plan generation
- ✅ Benefits clearly explained
- ✅ Easy access to start questionnaire
- ✅ Comparison between basic and personalized results
- ✅ Option to disable reminders

### Reminder Flow:
```
📋 Basic Meal Plan Generated

Your 3-day plan is ready! For even better personalization:

🎯 Complete 2-minute setup for:
• Dietary restriction filtering
• Cuisine preference matching
• Cooking skill-appropriate recipes
• Goal-optimized nutrition targets

85% of users see improved meal satisfaction after setup.

[🚀 Quick Setup (2 min)] [⏸️ Remind Later] [❌ Don't Show Again]
```

---

## 🔧 Technical Implementation

### API Endpoints:
- `GET /nutrition-onboarding/questionnaire` - Get questionnaire structure
- `POST /nutrition-onboarding/responses` - Submit answers
- `GET /nutrition-onboarding/status` - Check completion status
- `POST /nutrition-onboarding/update-preferences` - Update specific preferences
- `POST /nutrition-onboarding/check-profile-internal` - Bot integration check

### Database Changes:
- Extended `user_profiles` with 20+ preference fields
- New `nutrition_questionnaire_responses` table for detailed tracking
- Indexes for performance on frequently queried preference fields

### Bot Integration:
- `check_user_onboarding_status()` function in food plan handler
- `start_nutrition_onboarding()` function with WebApp integration
- Preference flags for quick meal customization decisions

---

## 📊 Success Metrics

- **Onboarding Completion Rate:** 85% target (industry standard: 60%)
- **Time to Complete:** Under 3 minutes for quick, 7 minutes for full
- **User Satisfaction:** 4.5/5 stars for personalized vs 3.2/5 for basic plans
- **Plan Adherence:** 40% improvement with personalized recommendations
- **Feature Usage:** 70% of users modify preferences within first month