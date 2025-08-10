import 'package:dio/dio.dart';
import 'package:c0r_app/services/api/api_client.dart';

class ProfilesApi {
  final ApiClient _client;
  ProfilesApi(this._client);

  Future<void> saveProfile(Map<String, dynamic> profile) async {
    await _client.dio.post('/v1/app/profile', data: profile, options: Options(headers: {'Content-Type': 'application/json'}));
  }
}
