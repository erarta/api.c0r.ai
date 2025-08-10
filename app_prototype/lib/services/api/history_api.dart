import 'package:c0r_app/services/api/api_client.dart';

class HistoryApi {
  final ApiClient _client;
  HistoryApi(this._client);

  Future<List<Map<String, dynamic>>> list({String? cursor, int limit = 20}) async {
    final res = await _client.dio.get('/v1/app/history', queryParameters: {
      if (cursor != null) 'cursor': cursor,
      'limit': limit,
    });
    final data = res.data as Map<String, dynamic>;
    final items = (data['items'] as List?) ?? [];
    return items.cast<Map<String, dynamic>>();
  }
}
