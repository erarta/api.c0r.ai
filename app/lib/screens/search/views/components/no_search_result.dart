import 'package:flutter/material.dart';

import '../../../../constants.dart';

class NoSearchResult extends StatelessWidget {
  const NoSearchResult({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const SizedBox(height: defaultPadding),
        SizedBox(
          width: MediaQuery.of(context).size.width * 0.7,
          child: Image.asset(
            Theme.of(context).brightness == Brightness.dark
                ? "assets/Illustration/NoResultDarkTheme.png"
                : "assets/Illustration/NoResult.png",
          ),
        ),
        Text(
          "No search result",
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: defaultPadding / 2),
        const Text(
          "Customer network effects freemium. Advisor android paradigm shift product management. Customer disruptive crowdsource",
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}
