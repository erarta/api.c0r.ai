import 'package:flutter/material.dart';
import 'package:modera/route/route_constants.dart';

import '../../../../constants.dart';

class PayWithCash extends StatelessWidget {
  const PayWithCash({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
        child: Column(
          children: [
            const Spacer(),
            Image.asset(
              Theme.of(context).brightness == Brightness.dark
                  ? "assets/Illustration/PayWithCash_darkTheme.png"
                  : "assets/Illustration/PayWithCash_lightTheme.png",
              width: MediaQuery.of(context).size.width * 0.55,
            ),
            const SizedBox(height: defaultPadding * 2),
            Text(
              "Pay with cash",
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: defaultPadding * 1.5),
            const Text(
              "a Modera refundable \$24.00 will be charged to use cash on delivery, if you want to save this amount please switch to Pay with Card.",
              textAlign: TextAlign.center,
            ),
            const Spacer(),
            SafeArea(
              child: Padding(
                padding: const EdgeInsets.symmetric(
                    horizontal: defaultPadding, vertical: defaultPadding / 2),
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(context, thanksForOrderScreenRoute);
                  },
                  child: const Text("Confirm"),
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}
