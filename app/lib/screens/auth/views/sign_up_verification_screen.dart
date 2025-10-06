import 'package:flutter/material.dart';
import 'package:modera/components/custom_modal_bottom_sheet.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/screen_export.dart';
import 'package:modera/screens/auth/views/components/sign_up_verification_otp_form.dart';

class SignUpVerificationScreen extends StatelessWidget {
  const SignUpVerificationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(defaultPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "Verification code",
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: defaultPadding / 2),
              const Text("We have sent the code verification to "),
              Row(
                children: [
                  Text(
                    "evgeniy@erarta.ai",
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                  TextButton(
                    onPressed: () {},
                    child: const Text("Change your email?"),
                  )
                ],
              ),
              const SignUpVerificationOtpForm(),
              const SizedBox(height: defaultPadding),
              const Center(
                child: Text.rich(
                  TextSpan(
                    text: "Resend code after ",
                    children: [
                      TextSpan(
                        text: "1:36",
                        style: TextStyle(
                            color: primaryColor, fontWeight: FontWeight.w500),
                      ),
                    ],
                  ),
                ),
              ),
              const Spacer(),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () {},
                      child: const Text("Resend"),
                    ),
                  ),
                  const SizedBox(width: defaultPadding),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () {
                        FocusScope.of(context).unfocus();
                        customModalBottomSheet(
                          context,
                          isDismissible: false,
                          child: SafeArea(
                            child: Padding(
                              padding: const EdgeInsets.all(defaultPadding),
                              child: Column(
                                children: [
                                  Image.asset(
                                    Theme.of(context).brightness ==
                                            Brightness.light
                                        ? "assets/Illustration/success.png"
                                        : "assets/Illustration/success_dark.png",
                                    height: MediaQuery.of(context).size.height *
                                        0.3,
                                  ),
                                  const Spacer(),
                                  Text(
                                    "Whoohooo!",
                                    style:
                                        Theme.of(context).textTheme.titleLarge,
                                  ),
                                  const SizedBox(height: defaultPadding / 2),
                                  const Text(
                                      "Your email has been verified succesfully."),
                                  const Spacer(),
                                  ElevatedButton(
                                    onPressed: () {
                                      Navigator.pushNamedAndRemoveUntil(
                                          context,
                                          entryPointScreenRoute,
                                          ModalRoute.withName(
                                              signUpVerificationScreenRoute));
                                    },
                                    child: const Text("Go to shopping"),
                                  )
                                ],
                              ),
                            ),
                          ),
                        );
                      },
                      child: const Text("Confirm"),
                    ),
                  )
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
