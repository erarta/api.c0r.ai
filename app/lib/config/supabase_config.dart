import 'package:supabase_flutter/supabase_flutter.dart';

class SupabaseConfig {
  static final supabaseClient = Supabase.instance.client;

  static bool isInitialized() {
    try {
      return Supabase.instance.client.auth.currentUser != null;
    } catch (e) {
      return false;
    }
  }

  // Development Supabase instance
  static const String url = String.fromEnvironment(
    'SUPABASE_URL',
    defaultValue: 'https://cadeererdjwemspkeriq.supabase.co'
  );

  static const String anonKey = String.fromEnvironment(
    'SUPABASE_ANON_KEY',
    defaultValue: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNhZGVlcmVyZGp3ZW1zcGtlcmlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5MzQ1NTUsImV4cCI6MjA2ODUxMDU1NX0.96o6G_9hCsGAdAxO_eZtsEKgNtWT9x7ZcydXCyTdOsg'
  );

  static const String storageBucket = String.fromEnvironment('R2_STORAGE_BUCKET');
} 