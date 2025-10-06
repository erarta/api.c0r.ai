import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:form_field_validator/form_field_validator.dart';

import '../../../../constants.dart';

class NewPassForm extends StatelessWidget {
  const NewPassForm({
    super.key,
    required this.formKey,
  });

  final GlobalKey formKey;

  @override
  Widget build(BuildContext context) {
    String pass = "";
    return Form(
      key: formKey,
      child: Column(
        children: [
          TextFormField(
            onSaved: (pass) {
              // Password
            },
            onChanged: (password) => pass = password,
            validator: passwordValidator.call,
            autofocus: true,
            obscureText: true,
            textInputAction: TextInputAction.next,
            decoration: InputDecoration(
              hintText: "New password",
              prefixIcon: Padding(
                padding:
                    const EdgeInsets.symmetric(vertical: defaultPadding * 0.75),
                child: SvgPicture.asset(
                  "assets/icons/Lock.svg",
                  height: 24,
                  width: 24,
                  colorFilter: ColorFilter.mode(
                      Theme.of(context)
                          .textTheme
                          .bodyLarge!
                          .color!
                          .withOpacity(0.3),
                      BlendMode.srcIn),
                ),
              ),
            ),
          ),
          const SizedBox(height: defaultPadding),
          TextFormField(
            onSaved: (pass) {
              pass = pass;
            },
            validator: (value) =>
                MatchValidator(errorText: "Passwords do not match")
                    .validateMatch(value!, pass),
            obscureText: true,
            decoration: InputDecoration(
              hintText: "New password again",
              prefixIcon: Padding(
                padding:
                    const EdgeInsets.symmetric(vertical: defaultPadding * 0.75),
                child: SvgPicture.asset(
                  "assets/icons/Lock.svg",
                  height: 24,
                  width: 24,
                  colorFilter: ColorFilter.mode(
                      Theme.of(context)
                          .textTheme
                          .bodyLarge!
                          .color!
                          .withOpacity(0.3),
                      BlendMode.srcIn),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
