import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/services/auth/auth_service.dart';
import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});
  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _loading = false;
  String? _error;

  Future<void> _signIn() async {
    setState(() { _loading = true; _error = null; });
    try {
      final url = dotenv.get('SUPABASE_URL');
      final key = dotenv.get('SUPABASE_ANON_KEY');
      final auth = await AuthService.init(url: url, anonKey: key);
      await auth.signInWithEmail(_email.text.trim(), _password.text);
      await ApiClient.create(auth: auth);
      if (!mounted) return;
      Navigator.of(context).pushReplacementNamed('/main');
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return AppScaffold(
      appBar: AppBar(title: Text(l10n.t('auth.title'))),
      showLoading: _loading,
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(controller: _email, keyboardType: TextInputType.emailAddress, decoration: InputDecoration(labelText: l10n.t('auth.email'))),
            const SizedBox(height: 12),
            TextField(controller: _password, obscureText: true, decoration: InputDecoration(labelText: l10n.t('auth.password'))),
            const SizedBox(height: 16),
            if (_error != null) const SizedBox() else const SizedBox.shrink(),
            const SizedBox(height: 8),
            SizedBox(width: double.infinity, child: FilledButton(onPressed: _signIn, child: Text(l10n.t('auth.sign_in')))),
            const SizedBox(height: 8),
            SizedBox(width: double.infinity, child: OutlinedButton(onPressed: () {}, child: Text(l10n.t('auth.google_soon')))),
            SizedBox(width: double.infinity, child: OutlinedButton(onPressed: () {}, child: Text(l10n.t('auth.apple_soon')))),
          ],
        ),
      ),
    );
  }
}
