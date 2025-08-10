import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:c0r_app/features/home/state/daily_provider.dart';
import 'package:c0r_app/services/api/models.dart';

void main() {
  test('DailySummaryNotifier initializes loading then can set data', () async {
    final container = ProviderContainer(overrides: [
      dailySummaryProvider.overrideWith((ref) => _FakeDailySummaryNotifier()),
    ]);

    final state = container.read(dailySummaryProvider);
    expect(state.isLoading, true);

    final notifier = container.read(dailySummaryProvider.notifier) as _FakeDailySummaryNotifier;
    final sample = DailySummary(date: '2025-01-01', total: Nutrition(calories: 100, proteins: 10, fats: 5, carbohydrates: 20));
    notifier.setSample(sample);

    await Future<void>.delayed(const Duration(milliseconds: 10));
    final loaded = container.read(dailySummaryProvider);
    expect(loaded.hasValue, true);
    expect(loaded.value!.total.calories, 100);
  });
}

class _FakeDailySummaryNotifier extends DailySummaryNotifier {
  _FakeDailySummaryNotifier() : super(autoLoad: false);
  void setSample(DailySummary summary) {
    state = AsyncValue.data(summary);
  }
}
