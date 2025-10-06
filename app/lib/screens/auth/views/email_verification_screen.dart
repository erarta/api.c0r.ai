import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/route_constants.dart';

class EmailVerificationScreen extends ConsumerWidget {
  final String email;

  const EmailVerificationScreen({
    super.key,
    required this.email,
  });

  Future<void> _openEmailApp() async {
    final Uri emailUri = Uri(scheme: 'mailto', path: email);
    if (await canLaunchUrl(emailUri)) {
      await launchUrl(emailUri);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(defaultPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Image or Icon
              Center(
                child: Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    color: primaryColor.withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.email_outlined,
                    size: 60,
                    color: primaryColor,
                  ),
                ),
              ),
              const SizedBox(height: defaultPadding * 2),

              // Title
              Center(
                child: Text(
                  "Check Your Email",
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
              const SizedBox(height: defaultPadding * 1.5),

              // Message
              Center(
                child: Column(
                  children: [
                    Text(
                      "We have sent a 6-digit code to",
                      style: Theme.of(context).textTheme.bodyLarge,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: defaultPadding / 2),
                    Text(
                      email,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        color: primaryColor,
                        fontWeight: FontWeight.w600,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: defaultPadding * 2.5),

              // Instructions
              Container(
                padding: const EdgeInsets.all(defaultPadding * 1.5),
                decoration: BoxDecoration(
                  color: Theme.of(context).scaffoldBackgroundColor,
                  borderRadius: BorderRadius.circular(defaultPadding / 2),
                  border: Border.all(
                    color: Theme.of(context).dividerColor,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Please:",
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: defaultPadding),
                    _buildStep(context, "1", "Check your email inbox"),
                    const SizedBox(height: defaultPadding),
                    _buildStep(context, "2", "Click the link in the email OR enter code manually"),
                    const SizedBox(height: defaultPadding),
                    _buildStep(context, "3", "You'll be automatically signed in"),
                  ],
                ),
              ),
              const Spacer(),

              // Buttons
              const SizedBox(height: defaultPadding),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(
                      context,
                      'email_otp_verification',
                      arguments: {'email': email},
                    );
                  },
                  child: const Text("Enter Code Manually"),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStep(BuildContext context, String number, String text) {
    return Row(
      children: [
        Container(
          width: 32,
          height: 32,
          decoration: const BoxDecoration(
            color: primaryColor,
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              number,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        const SizedBox(width: defaultPadding),
        Expanded(
          child: Text(
            text,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              fontSize: 16,
            ),
          ),
        ),
      ],
    );
  }
}
