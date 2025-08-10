import 'dart:convert';
import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/services/api/daily_api.dart';
import 'package:c0r_app/services/api/favorites_api.dart';
import 'package:c0r_app/services/api/recipes_api.dart';
import 'package:c0r_app/services/api/weight_logs_api.dart';
import 'package:c0r_app/services/api/analyze_api.dart';

typedef MockHandler = Response Function(RequestOptions);

Future<ApiClient> _clientWith(MockHandler handler) async {
  final c = await ApiClient.create();
  c.dio.interceptors.clear();
  c.dio.interceptors.add(InterceptorsWrapper(onRequest: (options, handlerNext) {
    final res = handler(options);
    handlerNext.resolve(res);
  }));
  return c;
}

Response _json(String body, {int status = 200, RequestOptions? options}) =>
    Response(requestOptions: options ?? RequestOptions(), data: json.decode(body), statusCode: status);

void main() {
  setUpAll(() async {
    dotenv.testLoad(fileInput: 'API_BASE_URL=http://localhost\n');
  });

  test('DailyApi.getDaily parses summary', () async {
    final client = await _clientWith((opts) => _json('{"date":"2025-01-01","calories":1500,"proteins":80,"fats":50,"carbohydrates":180}', options: opts));
    final api = DailyApi(client);
    final res = await api.getDaily();
    expect(res.total.calories, 1500);
  });

  test('FavoritesApi.list returns items', () async {
    final client = await _clientWith((opts) => _json('{"items":[{"id":"1","name":"Fav"}]}', options: opts));
    final api = FavoritesApi(client);
    final items = await api.list();
    expect(items.first['name'], 'Fav');
  });

  test('RecipesApi.list returns items', () async {
    final client = await _clientWith((opts) => _json('{"items":[{"id":"1","name":"Rec"}]}', options: opts));
    final api = RecipesApi(client);
    final items = await api.list();
    expect(items.first['name'], 'Rec');
  });

  test('WeightLogsApi.add posts data', () async {
    late RequestOptions seen;
    final client = await _clientWith((opts) {
      seen = opts;
      return _json('{}', options: opts);
    });
    final api = WeightLogsApi(client);
    await api.add(date: '2025-01-01', weightKg: 70.0);
    expect(seen.path.contains('/v1/app/weight-logs'), true);
  });

  test('AnalyzeApi.analyze posts multipart', () async {
    late RequestOptions seen;
    final client = await _clientWith((opts) {
      seen = opts;
      return _json('{"analysis":{"total_nutrition":{"calories":100,"proteins":1,"fats":2,"carbohydrates":3}},"daily_summary":{}}', options: opts);
    });
    final api = AnalyzeApi(client);
    final tmp = File('${Directory.systemTemp.path}/x.jpg');
    await tmp.writeAsBytes([0]);
    final res = await api.analyze(tmp);
    expect(seen.data is FormData, true);
    expect(res.analysis.total.calories, 100);
    await tmp.delete();
  });
}
