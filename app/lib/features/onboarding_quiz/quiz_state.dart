import 'package:flutter_riverpod/flutter_riverpod.dart';

class OnboardingAnswers {
  final String? gender;
  final String? activityLevel;
  final List<String> dietTypes;
  final List<String> tastePreferences;
  final List<String> allergens;
  final List<String> cuisines;
  final List<String> dislikedIngredients;
  final double? weightKg;
  final int? ageYears;

  const OnboardingAnswers({
    this.gender,
    this.activityLevel,
    this.dietTypes = const [],
    this.tastePreferences = const [],
    this.allergens = const [],
    this.cuisines = const [],
    this.dislikedIngredients = const [],
    this.weightKg,
    this.ageYears,
  });

  OnboardingAnswers copyWith({
    String? gender,
    String? activityLevel,
    List<String>? dietTypes,
    List<String>? tastePreferences,
    List<String>? allergens,
    List<String>? cuisines,
    List<String>? dislikedIngredients,
    double? weightKg,
    int? ageYears,
  }) {
    return OnboardingAnswers(
      gender: gender ?? this.gender,
      activityLevel: activityLevel ?? this.activityLevel,
      dietTypes: dietTypes ?? this.dietTypes,
      tastePreferences: tastePreferences ?? this.tastePreferences,
      allergens: allergens ?? this.allergens,
      cuisines: cuisines ?? this.cuisines,
      dislikedIngredients: dislikedIngredients ?? this.dislikedIngredients,
      weightKg: weightKg ?? this.weightKg,
      ageYears: ageYears ?? this.ageYears,
    );
  }

  Map<String, dynamic> toMap() {
    // Keys mirrored to Telegram bot profile schema (diet, tastes, allergens, cuisines, dislikes, weight_kg)
    return {
      'gender': gender,
      'activity_level': activityLevel,
      'diet': dietTypes,
      'tastes': tastePreferences,
      'allergens': allergens,
      'cuisines': cuisines,
      'dislikes': dislikedIngredients,
      'weight_kg': weightKg,
      'age': ageYears,
    };
  }
}

class OnboardingAnswersNotifier extends StateNotifier<OnboardingAnswers> {
  OnboardingAnswersNotifier() : super(const OnboardingAnswers());

  void updateGender(String value) => state = state.copyWith(gender: value);
  void updateActivityLevel(String value) => state = state.copyWith(activityLevel: value);
  void setDiet(List<String> values) => state = state.copyWith(dietTypes: values);
  void setTastes(List<String> values) => state = state.copyWith(tastePreferences: values);
  void setAllergens(List<String> values) => state = state.copyWith(allergens: values);
  void setCuisines(List<String> values) => state = state.copyWith(cuisines: values);
  void setDislikes(List<String> values) => state = state.copyWith(dislikedIngredients: values);
  void setWeightKg(double value) => state = state.copyWith(weightKg: value);
  void setAgeYears(int value) => state = state.copyWith(ageYears: value);
}

final onboardingAnswersProvider = StateNotifierProvider<OnboardingAnswersNotifier, OnboardingAnswers>((ref) {
  return OnboardingAnswersNotifier();
});

// Alias for consistency with screen naming
final quizStateProvider = onboardingAnswersProvider;


