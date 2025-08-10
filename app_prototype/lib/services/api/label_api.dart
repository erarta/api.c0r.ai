import 'dart:io';
import 'package:dio/dio.dart';
import 'package:c0r_app/services/api/api_client.dart';

class LabelApi {
  final ApiClient _client;
  LabelApi(this._client);

  Future<Map<String, dynamic>> analyze(File photo, {String? userLanguage}) async {
    final form = FormData.fromMap({
      'photo': await MultipartFile.fromFile(photo.path, filename: photo.uri.pathSegments.last),
      if (userLanguage != null) 'user_language': userLanguage,
    });
    final res = await _client.dio.post('/v1/app/label/analyze', data: form);
    return res.data as Map<String, dynamic>;
  }
}
