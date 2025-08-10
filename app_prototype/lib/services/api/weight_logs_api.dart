import 'package:c0r_app/services/api/api_client.dart';

class WeightLogsApi {
  final ApiClient _client;
  WeightLogsApi(this._client);

  Future<void> add({required String date, required double weightKg}) async {
    await _client.dio.post('/v1/app/weight-logs', data: {
      'date': date,
      'weight_kg': weightKg,
    });
  }

  Future<List<Map<String, dynamic>>> list({String? range}) async {
    final res = await _client.dio.get('/v1/app/weight-logs', queryParameters: {
      if (range != null) 'range': range,
    });
    final data = res.data as Map<String, dynamic>;
    return (data['items'] as List?)?.cast<Map<String, dynamic>>() ?? <Map<String, dynamic>>[];
  }
}
