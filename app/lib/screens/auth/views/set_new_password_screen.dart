import 'package:flutter/material.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/screen_export.dart';

import 'components/new_pass_form.dart';

class SetNewPasswordScreen extends StatelessWidget {
  const SetNewPasswordScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final GlobalKey<FormState> key = GlobalKey<FormState>();
    return Scaffold(
      appBar: AppBar(),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "Set new password",
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: defaultPadding / 2),
              const Text(
                  "Your new password must be diffrent from previosly used passwords."),
              const SizedBox(
                height: defaultPadding * 2,
              ),
              NewPassForm(formKey: key),
              const Spacer(),
              ElevatedButton(
                onPressed: () {
                  if (key.currentState!.validate()) {
                    Navigator.pushNamedAndRemoveUntil(context,
                        doneResetPasswordScreenRoute, (route) => false);
                  }
                },
                child: const Text("Change Password"),
              ),
              const SizedBox(height: defaultPadding),
            ],
          ),
        ),
      ),
    );
  }
}
