import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

// User state provider
final userProvider = StateNotifierProvider<UserNotifier, User?>((ref) {
  return UserNotifier();
});

class UserNotifier extends StateNotifier<User?> {
  UserNotifier() : super(null);

  // Method to set user
  void setUser(User? user) {
    state = user;
  }

  // Method to clear user (logout)
  void clearUser() {
    state = null;
  }
}

// Provider to check if user is authenticated
final isAuthenticatedProvider = Provider<bool>((ref) {
  return ref.watch(userProvider) != null;
}); 