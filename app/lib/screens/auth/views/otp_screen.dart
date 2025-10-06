import 'package:flutter/material.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/screen_export.dart';

import 'components/otp_form.dart';

class OtpScreen extends StatelessWidget {
  const OtpScreen({super.key});

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
                    "+99******1233",
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                  TextButton(
                    onPressed: () {},
                    child: const Text("Change phone number?"),
                  )
                ],
              ),
              const OtpForm(),
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
                        Navigator.pushNamed(context, newPasswordScreenRoute);
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
