import 'dart:io';
import 'package:dio/dio.dart';
import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/services/api/models.dart';

class AnalyzeApi {
  final ApiClient _client;
  AnalyzeApi(this._client);

  Future<AnalyzeResponse> analyze(File photo, {String? provider, String? userLanguage}) async {
    final form = FormData.fromMap({
      'photo': await MultipartFile.fromFile(photo.path, filename: photo.uri.pathSegments.last),
      if (provider != null) 'provider': provider,
      if (userLanguage != null) 'user_language': userLanguage,
    });
    final res = await _client.dio.post('/v1/analyze', data: form);
    return AnalyzeResponse.fromJson(res.data as Map<String, dynamic>);
  }
}
