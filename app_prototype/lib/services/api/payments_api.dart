import 'package:dio/dio.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:c0r_app/services/api/api_client.dart';

class PaymentsApi {
  final ApiClient _client;
  PaymentsApi(this._client);

  Future<void> buyCredits({
    required double amount,
    required String planId,
    Future<bool> Function(Uri uri)? openUrl,
  }) async {
    final res = await _client.dio.post('/v1/app/pay/invoice', data: {
      'amount': amount,
      'plan_id': planId,
      'description': 'Credits purchase',
    }, options: Options(headers: {'Content-Type': 'application/json'}));
    final data = res.data as Map<String, dynamic>;
    final url = data['confirmation_url'] as String?;
    if (url != null) {
      final uri = Uri.parse(url);
      if (openUrl != null) {
        await openUrl(uri);
        return;
      }
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      }
    }
  }
}
