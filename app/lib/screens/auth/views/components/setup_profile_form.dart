import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/features/onboarding_quiz/profile_basic_state.dart';

import '../../../../constants.dart';

class SetupProfileForm extends ConsumerWidget {
  const SetupProfileForm({
    super.key,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Form(
      child: Column(
        children: [
          TextFormField(
            decoration: InputDecoration(
              hintText: "Full name",
              prefixIcon: Padding(
                padding:
                    const EdgeInsets.symmetric(vertical: defaultPadding * 0.75),
                child: SvgPicture.asset(
                  "assets/icons/Profile.svg",
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
            onChanged: (v) => ref.read(profileBasicProvider.notifier).setName(v),
          ),
          const SizedBox(height: defaultPadding),
          // Removed DOB field per new requirement; DOB is collected in onboarding
          TextFormField(
            keyboardType: TextInputType.phone,
            decoration: InputDecoration(
              hintText: "Phone number",
              prefixIcon: Padding(
                padding: const EdgeInsets.only(left: defaultPadding),
                child: SizedBox(
                  width: 72,
                  child: Row(
                    children: [
                      SvgPicture.asset(
                        "assets/icons/Call.svg",
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
                      Padding(
                        padding: const EdgeInsets.symmetric(
                            horizontal: defaultPadding / 2),
                        child: Text(
                          "+1",
                          style:
                              Theme.of(context).inputDecorationTheme.hintStyle,
                        ),
                      ),
                      const SizedBox(
                        height: 24,
                        child: VerticalDivider(
                          thickness: 1,
                          width: defaultPadding / 2,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            onChanged: (v) => ref.read(profileBasicProvider.notifier).setPhone(v),
          ),
        ],
      ),
    );
  }
}
