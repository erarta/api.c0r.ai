import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/services/api/daily_api.dart';
import 'package:c0r_app/services/api/models.dart';

final dailySummaryProvider =
    StateNotifierProvider<DailySummaryNotifier, AsyncValue<DailySummary>>(
        (ref) => DailySummaryNotifier());

class DailySummaryNotifier extends StateNotifier<AsyncValue<DailySummary>> {
  DailySummaryNotifier({bool autoLoad = true}) : super(const AsyncValue.loading()) {
    if (autoLoad) {
      load();
    }
  }

  Future<void> load() async {
    try {
      final api = await ApiClient.create();
      final daily = DailyApi(api);
      final res = await daily.getDaily();
      state = AsyncValue.data(res);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}
