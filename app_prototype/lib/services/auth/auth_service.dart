import 'package:supabase_flutter/supabase_flutter.dart';

class AuthService {
  final SupabaseClient client;
  AuthService(this.client);

  static Future<AuthService> init({required String url, required String anonKey}) async {
    await Supabase.initialize(url: url, anonKey: anonKey);
    return AuthService(Supabase.instance.client);
  }

  String? get jwt => client.auth.currentSession?.accessToken;

  Future<void> signInWithEmail(String email, String password) async {
    final res = await client.auth.signInWithPassword(email: email, password: password);
    if (res.session == null) {
      throw Exception('Auth failed');
    }
  }

  Future<void> signOut() async {
    await client.auth.signOut();
  }
}
