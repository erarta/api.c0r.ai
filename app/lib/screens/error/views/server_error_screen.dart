import 'package:flutter/material.dart';

import '../../../constants.dart';

class ServerErrorScreen extends StatelessWidget {
  const ServerErrorScreen({super.key});

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
                    ? "assets/Illustration/server_error.png"
                    : "assets/Illustration/server_error_dark.png",
                height: MediaQuery.of(context).size.height * 0.3,
              ),
              const Spacer(),
              Text(
                "Server error \nplease try again later!",
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
