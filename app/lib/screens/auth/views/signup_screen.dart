import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:modera/screens/auth/views/components/sign_up_form.dart';
import 'package:modera/route/route_constants.dart';

import '../../../constants.dart';

class SignUpScreen extends StatefulWidget {
  const SignUpScreen({super.key});

  @override
  State<SignUpScreen> createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {
  final _formKey = GlobalKey<FormState>();
  String? errorMessage;

  Future<void> _signUp(String email) async {
    try {
      // Disable any ongoing interactions
      FocusManager.instance.primaryFocus?.unfocus();

      await SupabaseConfig.supabaseClient.auth.signInWithOtp(
        email: email,
        emailRedirectTo: 'ai.c0r.zer0://login-callback',
      );

      if (!mounted) return;

      // Debug logging
      print('🔐 OTP sent to: $email');

      // Navigate to email verification screen
      Navigator.pushNamed(
        context,
        signUpVerificationScreenRoute,
        arguments: {'email': email},
      );
    } on AuthException catch (e) {
      if (!mounted) return;

      setState(() {
        errorMessage = e.message;
      });
    } catch (e) {
      if (!mounted) return;

      setState(() {
        errorMessage = 'An unexpected error occurred';
      });
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        child: Column(
          children: [
            SizedBox(
              height: MediaQuery.of(context).size.height * 0.35,
              width: double.infinity,
              child: Image.asset(
                "assets/images/onboarding_2.jpeg",
                fit: BoxFit.cover,
                alignment: const Alignment(0, -0.95),
                errorBuilder: (context, error, stackTrace) {
                  return Container(
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.grey.shade800,
                          Colors.grey.shade900,
                        ],
                      ),
                    ),
                    child: Center(
                      child: Icon(
                        Icons.restaurant,
                        size: 100,
                        color: Colors.white.withOpacity(0.3),
                      ),
                    ),
                  );
                },
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(defaultPadding),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "Let's get started!",
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: defaultPadding / 2),
                  const Text(
                    "Please enter your valid data in order to create an account.",
                  ),
                  const SizedBox(height: defaultPadding),
                  SignUpForm(
                    formKey: _formKey,
                    onSaved: _signUp,
                  ),
                  const SizedBox(height: defaultPadding * 1.5),
                  if (errorMessage != null)
                    SelectableText.rich(
                      TextSpan(
                        text: errorMessage,
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),
                  const SizedBox(height: defaultPadding * 2),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text("Do you have an account?"),
                      TextButton(
                        onPressed: () {
                          Navigator.pushNamed(context, logInScreenRoute);
                        },
                        child: const Text("Log in"),
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
