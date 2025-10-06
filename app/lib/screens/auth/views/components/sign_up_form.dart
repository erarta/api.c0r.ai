import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../../../../constants.dart';

class SignUpForm extends StatelessWidget {
  const SignUpForm({
    super.key,
    required this.formKey,
    required this.onSaved,
  });

  final GlobalKey<FormState> formKey;
  final void Function(String email) onSaved;

  @override
  Widget build(BuildContext context) {
    String? email;

    return Form(
      key: formKey,
      child: Column(
        children: [
          TextFormField(
            onSaved: (value) => email = value,
            validator: emaildValidator.call,
            textInputAction: TextInputAction.done,
            keyboardType: TextInputType.emailAddress,
            decoration: InputDecoration(
              hintText: "Email address",
              prefixIcon: Padding(
                padding: const EdgeInsets.symmetric(vertical: defaultPadding * 0.75),
                child: SvgPicture.asset(
                  "assets/icons/Message.svg",
                  height: 24,
                  width: 24,
                  colorFilter: ColorFilter.mode(
                    Theme.of(context).textTheme.bodyLarge!.color!.withOpacity(0.3),
                    BlendMode.srcIn,
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: defaultPadding * 2),
          ElevatedButton(
            onPressed: () {
              if (formKey.currentState!.validate()) {
                formKey.currentState!.save();
                onSaved(email!);
              }
            },
            child: const Text("Continue"),
          ),
        ],
      ),
    );
  }
}
