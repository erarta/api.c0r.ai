import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/route_constants.dart';
import 'dart:async';

class EmailOtpVerificationScreen extends ConsumerStatefulWidget {
  final String email;

  const EmailOtpVerificationScreen({
    super.key,
    required this.email,
  });

  @override
  ConsumerState<EmailOtpVerificationScreen> createState() =>
      _EmailOtpVerificationScreenState();
}

class _EmailOtpVerificationScreenState
    extends ConsumerState<EmailOtpVerificationScreen>
    with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final List<TextEditingController> _controllers =
      List.generate(6, (_) => TextEditingController());
  final List<FocusNode> _focusNodes = List.generate(6, (_) => FocusNode());
  bool _isLoading = false;
  String? _errorMessage;
  late AnimationController _shakeController;
  late Animation<double> _shakeAnimation;

  @override
  void initState() {
    super.initState();
    _shakeController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    _shakeAnimation = Tween<double>(begin: 0, end: 10).animate(
      CurvedAnimation(
        parent: _shakeController,
        curve: Curves.elasticIn,
      ),
    );
  }

  @override
  void dispose() {
    _shakeController.dispose();
    for (var controller in _controllers) {
      controller.dispose();
    }
    for (var node in _focusNodes) {
      node.dispose();
    }
    super.dispose();
  }

  void _triggerShakeAnimation() {
    _shakeController.forward(from: 0).then((_) {
      _shakeController.reverse();
    });
  }

  void _clearOtpFields() {
    for (var controller in _controllers) {
      controller.clear();
    }
    _focusNodes[0].requestFocus();
  }

  String get _otpCode {
    return _controllers.map((c) => c.text).join();
  }

  void _handlePaste(String pastedText) {
    // Extract only digits from pasted text
    final digitsOnly = pastedText.replaceAll(RegExp(r'\D'), '');

    // Take first 6 digits
    final code = digitsOnly.substring(0, digitsOnly.length > 6 ? 6 : digitsOnly.length);

    // Fill the text fields
    for (int i = 0; i < code.length && i < 6; i++) {
      _controllers[i].text = code[i];
    }

    // If we have all 6 digits, unfocus and verify
    if (code.length == 6) {
      _focusNodes[5].unfocus();
      // Auto-verify after a short delay to let UI update
      Future.delayed(const Duration(milliseconds: 100), () {
        _verifyOtp();
      });
    } else if (code.length > 0 && code.length < 6) {
      // Focus on the next empty field
      _focusNodes[code.length].requestFocus();
    }
  }

  Future<void> _verifyOtp() async {
    if (_otpCode.length != 6) {
      setState(() {
        _errorMessage = 'Please enter the complete 6-digit code';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final response = await Supabase.instance.client.auth.verifyOTP(
        type: OtpType.email,
        token: _otpCode,
        email: widget.email,
      );

      if (!mounted) return;

      if (response.session != null) {
        // Successfully verified - navigation will be handled by auth listener in main.dart
        Navigator.pushNamedAndRemoveUntil(
          context,
          entryPointScreenRoute,
          (route) => false,
        );
      } else {
        // Invalid code - shake and clear
        setState(() {
          _errorMessage = 'Oops! That code doesn\'t match. Let\'s try again.';
          _isLoading = false;
        });
        _triggerShakeAnimation();
        Future.delayed(const Duration(milliseconds: 600), () {
          _clearOtpFields();
        });
      }
    } catch (e) {
      if (!mounted) return;

      // Error - shake and clear
      setState(() {
        _errorMessage = 'Hmm, that code didn\'t work. Try again or request a new one.';
        _isLoading = false;
      });
      _triggerShakeAnimation();
      Future.delayed(const Duration(milliseconds: 600), () {
        _clearOtpFields();
      });
    }
  }

  Future<void> _resendCode() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await Supabase.instance.client.auth.signInWithOtp(
        email: widget.email,
        emailRedirectTo: 'ai.c0r.zer0://login-callback',
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Verification code sent to your email'),
          backgroundColor: primaryColor,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _errorMessage = 'Failed to resend code. Please try again.';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
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
              Text(
                "Enter Verification Code",
                style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: defaultPadding),
              Text(
                "We have sent a 6-digit code to",
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              const SizedBox(height: defaultPadding / 2),
              Text(
                widget.email,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: primaryColor,
                      fontWeight: FontWeight.w600,
                    ),
              ),
              const SizedBox(height: defaultPadding * 2),
              AnimatedBuilder(
                animation: _shakeAnimation,
                builder: (context, child) {
                  return Transform.translate(
                    offset: Offset(
                      sin(_shakeController.value * pi * 4) * _shakeAnimation.value,
                      0,
                    ),
                    child: child,
                  );
                },
                child: Form(
                  key: _formKey,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: List.generate(6, (index) {
                      return SizedBox(
                        height: 64,
                        width: 48,
                        child: TextFormField(
                          controller: _controllers[index],
                          focusNode: _focusNodes[index],
                          autofocus: index == 0,
                          autofillHints: index == 0 ? const [AutofillHints.oneTimeCode] : null,
                          onChanged: (value) {
                            print('🔢 Field $index changed: "$value" (length: ${value.length})');
                            // Handle paste - if multiple digits pasted
                            if (value.length > 1) {
                              print('📋 Pasting: $value');
                              _handlePaste(value);
                              return;
                            }

                            if (value.length == 1) {
                              if (index < 5) {
                                _focusNodes[index + 1].requestFocus();
                              } else {
                                _focusNodes[index].unfocus();
                                // Auto-verify when last digit is entered
                                _verifyOtp();
                              }
                            } else if (value.isEmpty && index > 0) {
                              _focusNodes[index - 1].requestFocus();
                            }
                          },
                          style: Theme.of(context).textTheme.headlineSmall,
                          textAlign: TextAlign.center,
                          maxLength: null,
                          decoration: const InputDecoration(
                            counterText: "",
                          ),
                          keyboardType: TextInputType.number,
                          inputFormatters: [
                            FilteringTextInputFormatter.digitsOnly,
                            LengthLimitingTextInputFormatter(1),
                          ],
                        ),
                      );
                    }),
                  ),
                ),
              ),
              if (_errorMessage != null) ...[
                const SizedBox(height: defaultPadding),
                Container(
                  padding: const EdgeInsets.all(defaultPadding * 1.2),
                  decoration: BoxDecoration(
                    color: Colors.orange.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: Colors.orange.withOpacity(0.3),
                      width: 1.5,
                    ),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(Icons.info_outline, color: Colors.orange.shade700, size: 24),
                      const SizedBox(width: defaultPadding / 2),
                      Expanded(
                        child: Text(
                          _errorMessage!,
                          style: TextStyle(
                            color: Colors.orange.shade900,
                            fontSize: 15,
                            fontWeight: FontWeight.w500,
                            height: 1.4,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
              const Spacer(),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: _isLoading ? null : _resendCode,
                      child: const Text("Resend Code"),
                    ),
                  ),
                  const SizedBox(width: defaultPadding),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _verifyOtp,
                      child: _isLoading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor:
                                    AlwaysStoppedAnimation<Color>(Colors.white),
                              ),
                            )
                          : const Text("Verify"),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
