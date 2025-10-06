import 'package:flutter/material.dart';
import 'package:modera/constants.dart';

class EmptyPaymentScreen extends StatelessWidget {
  const EmptyPaymentScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Payment"),
      ),
      body: SafeArea(
        child: Column(
          children: [
            const Spacer(flex: 2),
            Image.asset(
              Theme.of(context).brightness == Brightness.light
                  ? "assets/Illustration/EmptyState_lightTheme.png"
                  : "assets/Illustration/EmptyState_darkTheme.png",
              width: MediaQuery.of(context).size.width * 0.7,
            ),
            const Spacer(),
            Text(
              "Empty payment",
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const Padding(
              padding: EdgeInsets.symmetric(
                  horizontal: defaultPadding * 1.5, vertical: defaultPadding),
              child: Text(
                "Customer network effects freemium. Advisor android paradigm shift product management. Customer disruptive crowdsource",
                textAlign: TextAlign.center,
              ),
            ),
            const Spacer(flex: 2),
          ],
        ),
      ),
    );
  }
}
