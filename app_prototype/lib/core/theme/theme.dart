import 'package:flutter/material.dart';
import 'package:c0r_app/core/theme/tokens.dart';

@immutable
class NutritionColors extends ThemeExtension<NutritionColors> {
  final Color calories;
  final Color proteins;
  final Color fats;
  final Color carbs;

  const NutritionColors({
    required this.calories,
    required this.proteins,
    required this.fats,
    required this.carbs,
  });

  @override
  NutritionColors copyWith({
    Color? calories,
    Color? proteins,
    Color? fats,
    Color? carbs,
  }) => NutritionColors(
        calories: calories ?? this.calories,
        proteins: proteins ?? this.proteins,
        fats: fats ?? this.fats,
        carbs: carbs ?? this.carbs,
      );

  @override
  ThemeExtension<NutritionColors> lerp(
      covariant ThemeExtension<NutritionColors>? other, double t) {
    if (other is! NutritionColors) return this;
    return NutritionColors(
      calories: Color.lerp(calories, other.calories, t)!,
      proteins: Color.lerp(proteins, other.proteins, t)!,
      fats: Color.lerp(fats, other.fats, t)!,
      carbs: Color.lerp(carbs, other.carbs, t)!,
    );
  }
}

ThemeData buildLightTheme() {
  final colorScheme = ColorScheme.fromSeed(
    seedColor: const Color(AppColorsLight.primary),
    brightness: Brightness.light,
  ).copyWith(
    primary: const Color(AppColorsLight.primary),
    onPrimary: const Color(AppColorsLight.onPrimary),
    secondary: const Color(AppColorsLight.carbs),
    surface: const Color(AppColorsLight.surface),
    onSurface: const Color(AppColorsLight.text),
    error: const Color(AppColorsLight.error),
  );

  return ThemeData(
    colorScheme: colorScheme,
    scaffoldBackgroundColor: const Color(AppColorsLight.background),
    useMaterial3: true,
    textTheme: const TextTheme(
      displayLarge: TextStyle(fontSize: AppTypography.h1, fontWeight: FontWeight.w700),
      titleLarge: TextStyle(fontSize: AppTypography.h2, fontWeight: FontWeight.w600),
      titleMedium: TextStyle(fontSize: AppTypography.h3, fontWeight: FontWeight.w600),
      bodyLarge: TextStyle(fontSize: AppTypography.body, fontWeight: FontWeight.w400),
      bodyMedium: TextStyle(fontSize: AppTypography.bodySm, fontWeight: FontWeight.w400),
      labelSmall: TextStyle(fontSize: AppTypography.caption, fontWeight: FontWeight.w400),
    ),
    appBarTheme: const AppBarTheme(
      centerTitle: true,
      elevation: 0,
      surfaceTintColor: Colors.transparent,
      backgroundColor: Color(AppColorsLight.surface),
      foregroundColor: Color(AppColorsLight.text),
    ),
    cardTheme: CardThemeData(
      color: const Color(AppColorsLight.surface),
      elevation: AppElevation.card,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.lg)),
      surfaceTintColor: Colors.transparent,
      margin: EdgeInsets.zero,
    ),
    chipTheme: const ChipThemeData(
      backgroundColor: Color(0xFFF1F5F9),
      labelStyle: TextStyle(fontSize: AppTypography.bodySm),
      side: BorderSide(color: Color(0xFFE2E8F0)),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: const Color(0xFFF8FAFC),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.lg),
        borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.lg),
        borderSide: const BorderSide(color: Color(0xFFE2E8F0)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.lg),
        borderSide: const BorderSide(color: Color(AppColorsLight.primary)),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: const Color(AppColorsLight.primary),
        foregroundColor: const Color(AppColorsLight.onPrimary),
        minimumSize: const Size(double.infinity, 52),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.lg)),
        textStyle: const TextStyle(fontSize: AppTypography.body, fontWeight: FontWeight.w600),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        minimumSize: const Size(double.infinity, 52),
        side: const BorderSide(color: Color(0xFFE2E8F0)),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.lg)),
        textStyle: const TextStyle(fontSize: AppTypography.body, fontWeight: FontWeight.w600),
      ),
    ),
    navigationBarTheme: const NavigationBarThemeData(
      backgroundColor: Color(AppColorsLight.surface),
      indicatorColor: Color(0xFFEFF6FF),
      labelTextStyle: WidgetStatePropertyAll(TextStyle(fontSize: AppTypography.bodySm)),
    ),
    segmentedButtonTheme: SegmentedButtonThemeData(
      style: ButtonStyle(
        shape: WidgetStatePropertyAll(
          RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.md)),
        ),
        side: const WidgetStatePropertyAll(BorderSide(color: Color(0xFFE2E8F0))),
        padding: const WidgetStatePropertyAll(EdgeInsets.symmetric(horizontal: 8, vertical: 8)),
      ),
    ),
    extensions: const [
      NutritionColors(
        calories: Color(AppColorsLight.calories),
        proteins: Color(AppColorsLight.proteins),
        fats: Color(AppColorsLight.fats),
        carbs: Color(AppColorsLight.carbs),
      ),
    ],
  );
}

ThemeData buildDarkTheme() {
  final colorScheme = ColorScheme.fromSeed(
    seedColor: const Color(AppColorsDark.primary),
    brightness: Brightness.dark,
  ).copyWith(
    primary: const Color(AppColorsDark.primary),
    onPrimary: const Color(AppColorsDark.onPrimary),
    secondary: const Color(AppColorsDark.carbs),
    surface: const Color(AppColorsDark.surface),
    onSurface: const Color(AppColorsDark.text),
    error: const Color(AppColorsDark.error),
  );

  return ThemeData(
    colorScheme: colorScheme,
    scaffoldBackgroundColor: const Color(AppColorsDark.background),
    useMaterial3: true,
    textTheme: const TextTheme(
      displayLarge: TextStyle(fontSize: AppTypography.h1, fontWeight: FontWeight.w700),
      titleLarge: TextStyle(fontSize: AppTypography.h2, fontWeight: FontWeight.w600),
      titleMedium: TextStyle(fontSize: AppTypography.h3, fontWeight: FontWeight.w600),
      bodyLarge: TextStyle(fontSize: AppTypography.body, fontWeight: FontWeight.w400),
      bodyMedium: TextStyle(fontSize: AppTypography.bodySm, fontWeight: FontWeight.w400),
      labelSmall: TextStyle(fontSize: AppTypography.caption, fontWeight: FontWeight.w400),
    ),
    appBarTheme: const AppBarTheme(
      centerTitle: true,
      elevation: 0,
      surfaceTintColor: Colors.transparent,
      backgroundColor: Color(AppColorsDark.surface),
      foregroundColor: Color(AppColorsDark.text),
    ),
    cardTheme: CardThemeData(
      color: const Color(AppColorsDark.surface),
      elevation: AppElevation.card,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.lg)),
      surfaceTintColor: Colors.transparent,
      margin: EdgeInsets.zero,
    ),
    chipTheme: const ChipThemeData(
      backgroundColor: Color(0xFF0F172A),
      labelStyle: TextStyle(fontSize: AppTypography.bodySm),
      side: BorderSide(color: Color(0xFF1F2937)),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: const Color(0xFF0F172A),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.lg),
        borderSide: const BorderSide(color: Color(0xFF1F2937)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.lg),
        borderSide: const BorderSide(color: Color(0xFF1F2937)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(AppRadius.lg),
        borderSide: const BorderSide(color: Color(AppColorsDark.primary)),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: const Color(AppColorsDark.primary),
        foregroundColor: const Color(AppColorsDark.onPrimary),
        minimumSize: const Size(double.infinity, 52),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.lg)),
        textStyle: const TextStyle(fontSize: AppTypography.body, fontWeight: FontWeight.w600),
      ),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        minimumSize: const Size(double.infinity, 52),
        side: const BorderSide(color: Color(0xFF1F2937)),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.lg)),
        textStyle: const TextStyle(fontSize: AppTypography.body, fontWeight: FontWeight.w600),
      ),
    ),
    navigationBarTheme: const NavigationBarThemeData(
      backgroundColor: Color(AppColorsDark.surface),
      indicatorColor: Color(0xFF0B1220),
      labelTextStyle: WidgetStatePropertyAll(TextStyle(fontSize: AppTypography.bodySm)),
    ),
    segmentedButtonTheme: SegmentedButtonThemeData(
      style: ButtonStyle(
        shape: WidgetStatePropertyAll(
          RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppRadius.md)),
        ),
        side: const WidgetStatePropertyAll(BorderSide(color: Color(0xFF1F2937))),
        padding: const WidgetStatePropertyAll(EdgeInsets.symmetric(horizontal: 8, vertical: 8)),
      ),
    ),
    extensions: const [
      NutritionColors(
        calories: Color(AppColorsDark.calories),
        proteins: Color(AppColorsDark.proteins),
        fats: Color(AppColorsDark.fats),
        carbs: Color(AppColorsDark.carbs),
      ),
    ],
  );
}
