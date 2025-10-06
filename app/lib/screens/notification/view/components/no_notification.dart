import 'package:flutter/material.dart';

import '../../../../constants.dart';

class NoNotification extends StatelessWidget {
  const NoNotification({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Spacer(flex: 2),
        Image.asset(
          Theme.of(context).brightness == Brightness.light
              ? "assets/Illustration/NoResult.png"
              : "assets/Illustration/NoResultDarkTheme.png",
          width: MediaQuery.of(context).size.width * 0.7,
        ),
        const Spacer(),
        Text(
          "No notification",
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: defaultPadding / 1),
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: defaultPadding * 1.5),
          child: Text(
            "Customer network effects freemium. Advisor android paradigm shift product management. Customer disruptive crowdsource",
            textAlign: TextAlign.center,
          ),
        ),
        const Spacer(flex: 2),
      ],
    );
  }
}
