import 'package:flutter_test/flutter_test.dart';
import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/services/api/payments_api.dart';
import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

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

Response _json(Map<String, dynamic> data, {RequestOptions? options}) =>
    Response(requestOptions: options ?? RequestOptions(), data: data, statusCode: 200);

void main() {
  setUpAll(() {
    dotenv.testLoad(fileInput: 'API_BASE_URL=http://localhost\n');
  });

  test('PaymentsApi launches confirmation URL (injected)', () async {
    Uri? seen;
    final client = await _clientWith((opts) => _json({'confirmation_url': 'https://pay.example/confirm'}, options: opts));
    final api = PaymentsApi(client);
    await api.buyCredits(amount: 9.99, planId: 'basic', openUrl: (uri) async {
      seen = uri;
      return true;
    });
    expect(seen.toString(), 'https://pay.example/confirm');
  });
}
