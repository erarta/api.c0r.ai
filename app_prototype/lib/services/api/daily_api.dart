import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/services/api/models.dart';

class DailyApi {
  final ApiClient _client;
  DailyApi(this._client);

  Future<DailySummary> getDaily({String? date}) async {
    final res = await _client.dio.get('/v1/app/daily', queryParameters: {if (date != null) 'date': date});
    return DailySummary.fromJson(res.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> getProgress({required String range}) async {
    final res = await _client.dio.get('/v1/app/progress', queryParameters: {'range': range});
    return res.data as Map<String, dynamic>;
  }
}
