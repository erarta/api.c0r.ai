import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:modera/config/supabase_config.dart';

/// Centralized Supabase service for all database and auth operations
class SupabaseService {
  static SupabaseClient get client => Supabase.instance.client;

  // Auth operations
  static GoTrueClient get auth => client.auth;

  // Database operations
  static SupabaseQueryBuilder table(String tableName) => client.from(tableName);

  // Storage operations
  static SupabaseStorageClient get storage => client.storage;

  // Check if user is authenticated
  static bool get isAuthenticated => auth.currentUser != null;

  // Get current user
  static User? get currentUser => auth.currentUser;

  // Get current session
  static Session? get currentSession => auth.currentSession;

  /// Initialize Supabase with config
  static Future<void> initialize() async {
    await Supabase.initialize(
      url: SupabaseConfig.url,
      anonKey: SupabaseConfig.anonKey,
    );
  }

  /// Sign up with email and password
  static Future<AuthResponse> signUp({
    required String email,
    required String password,
    Map<String, dynamic>? data,
  }) async {
    return await auth.signUp(
      email: email,
      password: password,
      data: data,
    );
  }

  /// Sign in with email and password
  static Future<AuthResponse> signIn({
    required String email,
    required String password,
  }) async {
    return await auth.signInWithPassword(
      email: email,
      password: password,
    );
  }

  /// Sign out
  static Future<void> signOut() async {
    await auth.signOut();
  }

  /// Reset password
  static Future<void> resetPassword(String email) async {
    await auth.resetPasswordForEmail(email);
  }

  /// Update user data
  static Future<UserResponse> updateUser({
    String? email,
    String? password,
    Map<String, dynamic>? data,
  }) async {
    return await auth.updateUser(
      UserAttributes(
        email: email,
        password: password,
        data: data,
      ),
    );
  }

  /// Listen to auth state changes
  static Stream<AuthState> get authStateChanges => auth.onAuthStateChange;

  /// Upload file to storage
  static Future<String> uploadFile({
    required String bucket,
    required String path,
    required List<int> fileBytes,
    String? contentType,
  }) async {
    await storage.from(bucket).uploadBinary(
      path,
      fileBytes,
      fileOptions: FileOptions(contentType: contentType),
    );

    return storage.from(bucket).getPublicUrl(path);
  }

  /// Get public URL for file
  static String getPublicUrl(String bucket, String path) {
    return storage.from(bucket).getPublicUrl(path);
  }
}
