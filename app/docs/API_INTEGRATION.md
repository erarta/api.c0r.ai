# 🔌 API Integration Guide: Telegram Bot → Flutter App

## 🎯 **Overview**
This guide details how to integrate existing Telegram bot APIs with the Flutter app, maximizing reuse of proven food analysis infrastructure.

---

## 📊 **Existing API Analysis**

### **✅ Ready-to-Use Endpoints**

#### **Food Plan Generation**
```python
# services/api/public/routers/food_plan.py

POST /food-plan/generate
- ✅ Generates personalized meal plans
- ✅ Uses user profile and food history
- ✅ Returns 3-7 day plans with nutrition breakdown
- ✅ Includes shopping lists

GET /food-plan/current
- ✅ Gets current active meal plan
- ✅ Handles date-based plan retrieval
- ✅ Fallback to latest plan

POST /food-plan/generate-internal
- ✅ Internal API for bot integration
- ✅ Same functionality as public endpoint
- ✅ Requires internal auth headers
```

#### **Nutrition Onboarding**
```python
# services/api/public/routers/nutrition_onboarding.py

POST /nutrition-onboarding/check-profile-internal
- ✅ Checks if user completed onboarding
- ✅ Returns profile status and needs
- ✅ Used by bot for validation

# Additional onboarding endpoints available
- User profile creation
- Dietary preferences setup
- Health goals configuration
```

#### **Chat/AI Integration**
```python
# Current chat system in Flutter app
# services/api/messages → Food analysis queries

POST /api/messages
- ✅ Text message processing
- ✅ Audio transcription
- ✅ Product recommendations → Food recommendations
- ✅ Real-time responses
```

---

## 🔗 **Flutter Integration Strategy**

### **1. API Service Enhancement**

#### **Current API Service**
```dart
// lib/services/api_service.dart - CURRENT
class ApiService {
  static const String baseUrl = 'http://165.232.135.9:4242/';

  Future<Map<String, dynamic>?> sendTextMessage({
    required String userId,
    required String userMessage,
  });

  Future<Map<String, dynamic>?> transcribeAudioMessage({
    required String userId,
    required File audioFile,
  });
}
```

#### **Enhanced API Service**
```dart
// lib/services/api_service.dart - ENHANCED
class ApiService {
  static const String baseUrl = 'http://165.232.135.9:4242/';

  // EXISTING - Keep as is
  Future<Map<String, dynamic>?> sendTextMessage({...});
  Future<Map<String, dynamic>?> transcribeAudioMessage({...});

  // NEW - Food Plan Integration
  Future<Map<String, dynamic>?> generateFoodPlan({
    required String userId,
    int days = 3,
    bool force = false,
  }) async {
    final response = await _dio.post(
      '/food-plan/generate',
      data: {
        'user_id': userId,
        'days': days,
        'force': force,
      },
    );
    return response.data;
  }

  Future<Map<String, dynamic>?> getCurrentFoodPlan({
    required String userId,
  }) async {
    final response = await _dio.get('/food-plan/current');
    return response.data;
  }

  // NEW - Nutrition Profile
  Future<Map<String, dynamic>?> checkNutritionProfile({
    required String userId,
  }) async {
    final response = await _dio.post(
      '/nutrition-onboarding/check-profile-internal',
      data: {'user_id': userId},
      options: Options(headers: _getInternalHeaders()),
    );
    return response.data;
  }

  // NEW - Food Analysis
  Future<Map<String, dynamic>?> analyzeFood({
    required String userId,
    required File foodImage,
  }) async {
    final formData = FormData.fromMap({
      'user_id': userId,
      'file': await MultipartFile.fromFile(foodImage.path),
      'analysis_type': 'food_image',
    });

    final response = await _dio.post(
      '/api/food/analyze-image',  // New endpoint needed
      data: formData,
    );
    return response.data;
  }

  Map<String, String> _getInternalHeaders() {
    return {
      'X-Internal-API-Key': 'your-internal-key',
      'Content-Type': 'application/json',
    };
  }
}
```

---

### **2. Data Models**

#### **Food Plan Models**
```dart
// lib/models/food_plan.dart
class FoodPlan {
  final String id;
  final String userId;
  final String startDate;
  final String endDate;
  final Map<String, DayPlan> planJson;
  final ShoppingList shoppingList;
  final String? introSummary;
  final double confidence;
  final String modelUsed;

  factory FoodPlan.fromJson(Map<String, dynamic> json) {
    return FoodPlan(
      id: json['id'],
      userId: json['user_id'],
      startDate: json['start_date'],
      endDate: json['end_date'],
      planJson: (json['plan_json'] as Map<String, dynamic>)
          .map((k, v) => MapEntry(k, DayPlan.fromJson(v))),
      shoppingList: ShoppingList.fromJson(json['shopping_list_json']),
      introSummary: json['intro_summary'],
      confidence: json['confidence']?.toDouble() ?? 0.5,
      modelUsed: json['model_used'] ?? 'unknown',
    );
  }
}

class DayPlan {
  final Meal? breakfast;
  final Meal? lunch;
  final Meal? dinner;
  final Meal? snack;
  final DaySummary summary;

  factory DayPlan.fromJson(Map<String, dynamic> json) {
    return DayPlan(
      breakfast: json['breakfast'] != null ? Meal.fromJson(json['breakfast']) : null,
      lunch: json['lunch'] != null ? Meal.fromJson(json['lunch']) : null,
      dinner: json['dinner'] != null ? Meal.fromJson(json['dinner']) : null,
      snack: json['snack'] != null ? Meal.fromJson(json['snack']) : null,
      summary: DaySummary.fromJson(json['summary']),
    );
  }
}

class Meal {
  final String text;
  final int calories;
  final int protein;
  final int fats;
  final int carbs;
  final List<Ingredient> ingredients;

  factory Meal.fromJson(Map<String, dynamic> json) {
    return Meal(
      text: json['text'] ?? '',
      calories: json['calories'] ?? 0,
      protein: json['protein'] ?? 0,
      fats: json['fats'] ?? 0,
      carbs: json['carbs'] ?? 0,
      ingredients: (json['ingredients'] as List?)
          ?.map((i) => Ingredient.fromJson(i))
          .toList() ?? [],
    );
  }
}
```

#### **Nutrition Profile Models**
```dart
// lib/models/nutrition_profile.dart
class NutritionProfile {
  final String userId;
  final bool hasProfile;
  final bool needsOnboarding;
  final UserGoals? goals;
  final DietaryPreferences? preferences;
  final HealthMetrics? metrics;

  factory NutritionProfile.fromJson(Map<String, dynamic> json) {
    return NutritionProfile(
      userId: json['user_id'],
      hasProfile: json['has_profile'] ?? false,
      needsOnboarding: json['needs_onboarding'] ?? true,
      goals: json['goals'] != null ? UserGoals.fromJson(json['goals']) : null,
      preferences: json['preferences'] != null
          ? DietaryPreferences.fromJson(json['preferences']) : null,
      metrics: json['metrics'] != null
          ? HealthMetrics.fromJson(json['metrics']) : null,
    );
  }
}
```

---

### **3. State Management Integration**

#### **Food Plan Provider**
```dart
// lib/providers/food_plan_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

final foodPlanProvider = StateNotifierProvider<FoodPlanNotifier, FoodPlanState>((ref) {
  return FoodPlanNotifier(ref.read(apiServiceProvider));
});

class FoodPlanNotifier extends StateNotifier<FoodPlanState> {
  final ApiService _apiService;

  FoodPlanNotifier(this._apiService) : super(FoodPlanState.initial());

  Future<void> generatePlan({int days = 3, bool force = false}) async {
    state = state.copyWith(isLoading: true);

    try {
      final userId = await _getCurrentUserId();
      final result = await _apiService.generateFoodPlan(
        userId: userId,
        days: days,
        force: force,
      );

      if (result != null) {
        final plan = FoodPlan.fromJson(result);
        state = state.copyWith(
          currentPlan: plan,
          isLoading: false,
          error: null,
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> loadCurrentPlan() async {
    state = state.copyWith(isLoading: true);

    try {
      final userId = await _getCurrentUserId();
      final result = await _apiService.getCurrentFoodPlan(userId: userId);

      if (result != null && result.isNotEmpty) {
        final plan = FoodPlan.fromJson(result);
        state = state.copyWith(
          currentPlan: plan,
          isLoading: false,
        );
      } else {
        state = state.copyWith(
          currentPlan: null,
          isLoading: false,
        );
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }
}

class FoodPlanState {
  final FoodPlan? currentPlan;
  final bool isLoading;
  final String? error;

  FoodPlanState({
    this.currentPlan,
    required this.isLoading,
    this.error,
  });

  factory FoodPlanState.initial() {
    return FoodPlanState(isLoading: false);
  }

  FoodPlanState copyWith({
    FoodPlan? currentPlan,
    bool? isLoading,
    String? error,
  }) {
    return FoodPlanState(
      currentPlan: currentPlan ?? this.currentPlan,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}
```

---

### **4. Screen Integration Examples**

#### **Home Screen with Food Plan Data**
```dart
// lib/screens/home/views/nutrition_home_screen.dart
class NutritionHomeScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final foodPlanState = ref.watch(foodPlanProvider);
    final nutritionProfile = ref.watch(nutritionProfileProvider);

    return Scaffold(
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            // Daily Progress Banner (reuse BannerLStyle1)
            SliverToBoxAdapter(
              child: DailyProgressBanner(
                currentCalories: foodPlanState.currentPlan?.todayCalories ?? 0,
                targetCalories: nutritionProfile.value?.goals?.dailyCalories ?? 2000,
              ),
            ),

            // Recent Meals (reuse product card layout)
            SliverToBoxAdapter(
              child: RecentMealsSection(
                meals: foodPlanState.currentPlan?.todayMeals ?? [],
              ),
            ),

            // Nutrition Tips (reuse flash sale component)
            SliverToBoxAdapter(
              child: NutritionTipsSection(),
            ),
          ],
        ),
      ),
    );
  }
}
```

#### **Chat Screen Food Analysis**
```dart
// lib/screens/chat/views/chat_screen.dart - ENHANCED
class ChatScreen extends StatefulWidget {
  // Keep existing implementation
  // Add food analysis specific methods

  Future<void> _sendFoodAnalysisMessage(String message) async {
    // Reuse existing sendTextMessage with food context
    final response = await _apiService.sendTextMessage(
      userId: _currentUserId!,
      userMessage: message,
    );

    // Handle food-specific responses
    if (response != null && response['food_analysis'] != null) {
      final foodAnalysis = FoodAnalysis.fromJson(response['food_analysis']);

      setState(() {
        _messages.add(FoodAnalysisMessage(
          analysis: foodAnalysis,
          time: _getCurrentTime(),
        ));
      });
    }
  }
}
```

---

### **5. New Endpoints to Implement**

#### **Food Image Analysis**
```python
# services/api/public/routers/food_analysis.py - NEW

@router.post("/food/analyze-image")
async def analyze_food_image(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    auth: AuthContext = Depends(require_auth_context)
):
    """Analyze food image and return nutrition information"""

    # 1. Upload image to S3
    image_url = await upload_to_s3(file, f"food_images/{user_id}/")

    # 2. Process with ML model
    analysis_result = await ml_service.analyze_food_image(image_url)

    # 3. Save to food_entries table
    food_entry = {
        "user_id": user_id,
        "image_url": image_url,
        "food_name": analysis_result["food_name"],
        "calories": analysis_result["calories"],
        "nutrition_data": analysis_result["nutrition"],
        "confidence": analysis_result["confidence"]
    }

    entry_id = await supabase_service.create_food_entry(food_entry)

    return {
        "entry_id": entry_id,
        "food_analysis": analysis_result,
        "image_url": image_url
    }
```

#### **Food Search**
```python
@router.get("/food/search")
async def search_food(
    query: str,
    limit: int = 10,
    auth: AuthContext = Depends(require_auth_context)
):
    """Search food database"""
    results = await food_database.search(query, limit)
    return {"foods": results}
```

---

### **6. Migration Strategy**

#### **Phase 1: API Integration (Week 1)**
1. Enhance `ApiService` with food plan endpoints
2. Create data models for API responses
3. Set up Riverpod providers for food data

#### **Phase 2: Screen Updates (Week 2-3)**
1. Update chat screen for food analysis
2. Transform home screen to nutrition dashboard
3. Implement meal plan screen

#### **Phase 3: New Features (Week 4-5)**
1. Add food scanning functionality
2. Implement nutrition onboarding
3. Create food history tracking

#### **Phase 4: Polish (Week 6)**
1. Error handling and edge cases
2. Offline capabilities
3. Performance optimization

---

## 🔄 **Bot-to-App API Consistency**

### **Telegram Bot Flow**
```python
# Bot receives food question
user_message → check_onboarding → analyze_food → generate_plan → format_response

# App equivalent
user_input → check_profile → analyze_image → update_plan → display_results
```

### **Shared Data Sources**
- ✅ Same Supabase database
- ✅ Same user authentication
- ✅ Same food analysis models
- ✅ Same meal plan generation logic
- ✅ Same nutrition calculations

This ensures 100% consistency between bot and app experiences while maximizing code reuse.