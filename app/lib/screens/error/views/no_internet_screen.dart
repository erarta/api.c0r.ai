import 'package:flutter/material.dart';
import 'package:modera/constants.dart';

class NoInternetScreen extends StatelessWidget {
  const NoInternetScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(defaultPadding),
          child: Column(
            children: [
              const Spacer(flex: 2),
              Image.asset(
                Theme.of(context).brightness == Brightness.light
                    ? "assets/Illustration/no_internet.png"
                    : "assets/Illustration/no_internet_dark.png",
                height: MediaQuery.of(context).size.height * 0.3,
              ),
              const Spacer(),
              Text(
                "No internet \nplease try again later!",
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const Spacer(),
              ElevatedButton(
                onPressed: () {},
                child: const Text("Retry"),
              )
            ],
          ),
        ),
      ),
    );
  }
}
