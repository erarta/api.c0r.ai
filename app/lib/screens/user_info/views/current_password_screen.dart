import 'package:flutter/material.dart';

import 'package:flutter_svg/flutter_svg.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/route_constants.dart';

class CurrentPasswordScreen extends StatelessWidget {
  const CurrentPasswordScreen({super.key});

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
              const SizedBox(height: defaultPadding),
              Text(
                "Current Password",
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: defaultPadding / 2),
              const Text("Enter your current password to reset your password"),
              const SizedBox(height: defaultPadding * 2),
              Form(
                child: TextFormField(
                  autofocus: true,
                  obscureText: true,
                  onSaved: (emal) {
                    // Email
                  },
                  validator: emaildValidator.call,
                  decoration: InputDecoration(
                    hintText: "password",
                    prefixIcon: Padding(
                      padding: const EdgeInsets.symmetric(
                          vertical: defaultPadding * 0.75),
                      child: SvgPicture.asset(
                        "assets/icons/Lock.svg",
                        height: 24,
                        width: 24,
                        color: Theme.of(context)
                            .textTheme
                            .bodyLarge!
                            .color!
                            .withOpacity(0.3),
                      ),
                    ),
                  ),
                ),
              ),
              const Spacer(),
              ElevatedButton(
                onPressed: () {
                  Navigator.pushReplacementNamed(
                      context, newPasswordScreenRoute);
                },
                child: const Text("Next"),
              )
            ],
          ),
        ),
      ),
    );
  }
}
