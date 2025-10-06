import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/route_constants.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/providers/auth_provider.dart';

import 'components/login_form.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  String? _email;
  String? _password;
  String? _errorMessage;

  void _saveEmail(String? email) => _email = email;
  void _savePassword(String? password) => _password = password;

  Future<void> _login() async {
    if (_formKey.currentState!.validate()) {
      _formKey.currentState!.save();

      // Check Supabase initialization
      // if (!SupabaseConfig.isInitialized()) {
      //   setState(() {
      //     _errorMessage = 'Supabase not properly initialized';
      //   });
      //   return;
      // }

      try {
        final response = await SupabaseConfig.supabaseClient.auth.signInWithPassword(
          email: _email!,
          password: _password!,
        );

        // More robust null checking
        if (response.user == null && response.session == null) {
          setState(() {
            _errorMessage = 'Authentication failed. No user found.';
          });
          return;
        }

        if (!mounted) return;

        if (response.user != null) {
          // Store user in Riverpod provider
          ref.read(userProvider.notifier).setUser(response.user);

          Navigator.pushNamedAndRemoveUntil(
            context,
            entryPointScreenRoute,
            ModalRoute.withName(logInScreenRoute),
          );
        } else {
          setState(() {
            _errorMessage = 'Invalid login or password. Please try again';
          });
        }
      } on AuthException catch (authError) {
        // Specific Supabase auth error handling
        switch (authError.statusCode) {
          case '400':
            setState(() {
              _errorMessage = 'Invalid credentials. Please check and try again.';
            });
            break;
          case '401':
            setState(() {
              _errorMessage = 'Unauthorized. Please verify your credentials.';
            });
            break;
          default:
            setState(() {
              _errorMessage = authError.message;
            });
        }
      } catch (error) {
        // Log unexpected error
        print('Unexpected Error during login: $error');
        
        setState(() {
          _errorMessage = 'An unexpected error occurred';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final Size size = MediaQuery.of(context).size;

    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            Image.asset(
              "assets/images/login_dark.png",
              fit: BoxFit.cover,
            ),
            Padding(
              padding: const EdgeInsets.all(defaultPadding),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "Welcome back!",
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: defaultPadding / 2),
                  const Text(
                    "Log in with your data that you entered during registration.",
                  ),
                  const SizedBox(height: defaultPadding),
                  LogInForm(
                    formKey: _formKey,
                    onSaveEmail: _saveEmail,
                    onSavePassword: _savePassword,
                  ),
                  if (_errorMessage != null)
                    Padding(
                      padding: const EdgeInsets.only(top: defaultPadding),
                      child: SelectableText.rich(
                        TextSpan(
                          text: _errorMessage,
                          style: const TextStyle(color: Colors.red),
                        ),
                      ),
                    ),
                  Align(
                    child: TextButton(
                      child: const Text("Forgot password"),
                      onPressed: () {
                        Navigator.pushNamed(
                            context, passwordRecoveryScreenRoute);
                      },
                    ),
                  ),
                  SizedBox(
                    height: size.height > 700
                        ? size.height * 0.1
                        : defaultPadding,
                  ),
                  ElevatedButton(
                    onPressed: _login,
                    child: const Text("Log in"),
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text("Don't have an account?"),
                      TextButton(
                        onPressed: () {
                          Navigator.pushNamed(context, signUpScreenRoute);
                        },
                        child: const Text("Sign up"),
                      )
                    ],
                  ),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}
