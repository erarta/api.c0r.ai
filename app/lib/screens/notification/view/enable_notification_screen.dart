import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/screen_export.dart';

class EnableNotificationScreen extends StatelessWidget {
  const EnableNotificationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Notification"),
        actions: [
          IconButton(
            onPressed: () {},
            icon: SvgPicture.asset(
              "assets/icons/DotsV.svg",
              colorFilter: ColorFilter.mode(
                Theme.of(context).iconTheme.color!,
                BlendMode.srcIn,
              ),
            ),
          )
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: defaultPadding * 1.5),
          child: Column(
            children: [
              const Spacer(flex: 2),
              Image.asset(
                Theme.of(context).brightness == Brightness.dark
                    ? "assets/Illustration/TurnOnNotification_darkTheme.png"
                    : "assets/Illustration/TurnOnNotification_lightTheme.png",
                width: MediaQuery.of(context).size.width * 0.7,
              ),
              const Spacer(),
              Text(
                "Push Notifications are currently turned off",
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: defaultPadding),
              const Text(
                "Enabling push notifications allows us to send you info about our new products, sales, events and more!",
              ),
              const Spacer(),
              ElevatedButton(
                onPressed: () {
                  Navigator.pushNamed(context, notificationOptionsScreenRoute);
                },
                child: const Text("Enable Notification"),
              ),
              const SizedBox(height: defaultPadding),
            ],
          ),
        ),
      ),
    );
  }
}
