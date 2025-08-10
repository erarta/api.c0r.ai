import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:c0r_app/features/home/widgets/daily_summary_panel.dart';
import 'package:c0r_app/features/home/state/daily_provider.dart';
import 'package:c0r_app/services/api/models.dart';
import 'package:c0r_app/core/theme/theme.dart';

void main() {
  testWidgets('DailySummaryPanel shows MacroRow when data available', (tester) async {
    final sample = DailySummary(
      date: '2025-01-01',
      total: Nutrition(calories: 1234, proteins: 88, fats: 44, carbohydrates: 199),
    );

    await tester.pumpWidget(ProviderScope(
      overrides: [
        dailySummaryProvider.overrideWith((ref) => _FixedDailyNotifier(sample)),
      ],
      child: MaterialApp(theme: buildLightTheme(), home: const Scaffold(body: DailySummaryPanel())),
    ));

    expect(find.textContaining('1234'), findsOneWidget);
  });
}

class _FixedDailyNotifier extends DailySummaryNotifier {
  _FixedDailyNotifier(DailySummary summary) {
    state = AsyncValue.data(summary);
  }
}
