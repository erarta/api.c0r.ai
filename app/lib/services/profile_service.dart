import 'package:supabase_flutter/supabase_flutter.dart';
import 'dart:typed_data';
import 'package:modera/features/onboarding_quiz/quiz_state.dart';

class ProfileService {
  final SupabaseClient _db;
  ProfileService(this._db);

  User? get currentUser => _db.auth.currentUser;

  Future<AuthResponse> signUp({required String email, required String password}) {
    return _db.auth.signUp(email: email, password: password);
  }

  Future<AuthResponse> signIn({required String email, required String password}) {
    return _db.auth.signInWithPassword(email: email, password: password);
  }

  Future<void> upsertProfile(OnboardingAnswers ans, {String? locale, String units = 'metric'}) async {
    final user = _db.auth.currentUser;
    if (user == null) throw StateError('No auth user');
    final payload = {
      'user_id': user.id,
      'goal': null,
      'activity_level': null,
      'weight_kg': ans.weightKg,
      'height_cm': null,
      'dietary_preferences': ans.dietTypes,
      'allergies': ans.allergens,
      'locale': locale,
      'units': units,
      'updated_at': DateTime.now().toIso8601String(),
    };
    await _db.from('user_profiles').upsert(payload, onConflict: 'user_id');
  }

  Future<String> uploadAvatarBytes(String bucket, String path, Uint8List bytes, {String contentType = 'image/jpeg'}) async {
    final storage = _db.storage.from(bucket);
    await storage.uploadBinary(path, bytes, fileOptions: FileOptions(contentType: contentType, upsert: true));
    final publicUrl = storage.getPublicUrl(path);
    return publicUrl;
  }

  Future<void> saveContactInfo({required String fullName, required String phone, String? avatarUrl}) async {
    final user = _db.auth.currentUser;
    if (user == null) throw StateError('No auth user');
    await _db.from('users').upsert({
      'id': user.id,
      'phone_number': phone,
    }, onConflict: 'id');
    await _db.from('user_profiles').upsert({
      'user_id': user.id,
      'full_name': fullName,
      'avatar_url': avatarUrl,
      'updated_at': DateTime.now().toIso8601String(),
    }, onConflict: 'user_id');
  }
}


