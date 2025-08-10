import 'package:c0r_app/services/api/api_client.dart';

class RecipesApi {
  final ApiClient _client;
  RecipesApi(this._client);

  Future<List<Map<String, dynamic>>> list({int limit = 20, String? search}) async {
    final res = await _client.dio.get('/v1/app/recipes', queryParameters: {
      'limit': limit,
      if (search != null) 'search': search,
    });
    final data = res.data as Map<String, dynamic>;
    final items = (data['items'] as List?) ?? [];
    return items.cast<Map<String, dynamic>>();
  }

  Future<Map<String, dynamic>> save({required String name, required Map<String, dynamic> itemsJson}) async {
    final res = await _client.dio.post('/v1/app/recipes', data: {
      'name': name,
      'items_json': itemsJson,
    });
    return res.data as Map<String, dynamic>;
  }

  Future<void> delete(String id) async {
    await _client.dio.delete('/v1/app/recipes/$id');
  }
}
