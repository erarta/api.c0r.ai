import 'package:flutter/material.dart';

import '../../../../constants.dart';
import 'use_available_credit.dart';

class PayWithCredit extends StatelessWidget {
  const PayWithCredit({
    super.key,
    this.isInsufficientBalance = false,
  });

  final bool isInsufficientBalance;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
        child: Column(
          children: [
            const SizedBox(height: defaultPadding),
            UseAvailableCredit(
              availableBalance: 365.83,
              onChanged: (value) {},
              value: true,
            ),
            if (isInsufficientBalance) const Spacer(),
            if (isInsufficientBalance)
              Image.asset(
                Theme.of(context).brightness == Brightness.dark
                    ? "assets/Illustration/Failed_darkTheme.png"
                    : "assets/Illustration/Failed_lightTheme.png",
                width: MediaQuery.of(context).size.width * 0.45,
              ),
            if (isInsufficientBalance)
              Padding(
                padding: const EdgeInsets.only(
                    top: defaultPadding * 3, bottom: defaultPadding),
                child: Text("Credit is not enough",
                    style: Theme.of(context).textTheme.titleLarge),
              ),
            if (isInsufficientBalance)
              const Text(
                "Your Modera credit are not sufficient to pay for the order, please select an additional payment method to cover the balance of \$500",
                textAlign: TextAlign.center,
              ),
            const Spacer(),
            if (!isInsufficientBalance)
              SafeArea(
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: defaultPadding),
                  child: ElevatedButton(
                    onPressed: () {},
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
