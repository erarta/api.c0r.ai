import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:c0r_app/services/auth/auth_service.dart';

class ApiClient {
  final Dio _dio;

  ApiClient._(this._dio);

  static Future<ApiClient> create({AuthService? auth}) async {
    final baseUrl = dotenv.get('API_BASE_URL', fallback: 'http://localhost:8000');

    final dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 20),
      headers: {'Accept': 'application/json'},
    ));

    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        final token = auth?.jwt;
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (e, handler) {
        return handler.next(e);
      },
    ));

    return ApiClient._(dio);
  }

  Dio get dio => _dio;
}
