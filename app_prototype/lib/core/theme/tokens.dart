// Design tokens (light/dark), spacing, radii, shadows, typography

class AppSpacing {
  static const double xxs = 4;
  static const double xs = 8;
  static const double sm = 12;
  static const double md = 16;
  static const double lg = 20;
  static const double xl = 24;
  static const double xxl = 32;
}

class AppRadius {
  static const double sm = 8;
  static const double md = 12;
  static const double lg = 16;
  static const double xl = 24;
}

class AppElevation {
  static const double card = 2;
  static const double popup = 6;
}

class AppColorsLight {
  // Extract from design; placeholders for now
  static const int background = 0xFFF8F9FB;
  static const int surface = 0xFFFFFFFF;
  static const int primary = 0xFF3B82F6; // blue
  static const int primaryDark = 0xFF1D4ED8;
  static const int onPrimary = 0xFFFFFFFF;
  static const int text = 0xFF0F172A; // slate-900
  static const int textMuted = 0xFF475569; // slate-600
  static const int success = 0xFF16A34A;
  static const int warning = 0xFFF59E0B;
  static const int error = 0xFFDC2626;
  // Nutrition
  static const int calories = 0xFFF97316; // orange
  static const int proteins = 0xFF10B981; // green
  static const int fats = 0xFFEF4444; // red
  static const int carbs = 0xFF3B82F6; // blue
}

class AppColorsDark {
  static const int background = 0xFF0B1220;
  static const int surface = 0xFF121A2A;
  static const int primary = 0xFF60A5FA;
  static const int primaryDark = 0xFF3B82F6;
  static const int onPrimary = 0xFF0B1220;
  static const int text = 0xFFE2E8F0; // slate-200
  static const int textMuted = 0xFF94A3B8; // slate-400
  static const int success = 0xFF22C55E;
  static const int warning = 0xFFFBBF24;
  static const int error = 0xFFF87171;
  static const int calories = 0xFFF59E0B;
  static const int proteins = 0xFF34D399;
  static const int fats = 0xFFFB7185;
  static const int carbs = 0xFF60A5FA;
}

class AppTypography {
  // Wire real fonts later from assets/fonts
  // Example sizes; match design explicitly when font files provided
  static const double h1 = 28;
  static const double h2 = 22;
  static const double h3 = 18;
  static const double body = 16;
  static const double bodySm = 14;
  static const double caption = 12;
}
