import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/route_constants.dart';

class NotificationPermissionScreen extends StatelessWidget {
  const NotificationPermissionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        top: false,
        child: Column(
          children: [
            AspectRatio(
              aspectRatio: 1,
              child: Stack(
                children: [
                  Image.asset(
                    "assets/images/notification.png",
                    fit: BoxFit.cover,
                  ),
                  Positioned(
                    right: 0,
                    child: SafeArea(
                      child: TextButton(
                        onPressed: () {
                          Navigator.pushNamed(
                              context, preferredLanuageScreenRoute);
                        },
                        child: Text(
                          "Skip",
                          style: TextStyle(
                              color:
                                  Theme.of(context).textTheme.bodyLarge!.color),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: defaultPadding),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
                child: Column(
                  children: [
                    Text(
                      "Notify latest offers & product availability",
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: defaultPadding),
                    const Text(
                      "ba faal kardane notificatione Modera, zoodtar az hame az akhbare ma bakhabar shavid.",
                    ),
                    const Spacer(),
                    Container(
                      padding: const EdgeInsets.all(defaultPadding),
                      decoration: BoxDecoration(
                        color: Theme.of(context)
                            .textTheme
                            .bodyLarge!
                            .color!
                            .withOpacity(0.05),
                        borderRadius: const BorderRadius.all(
                            Radius.circular(defaultBorderRadious)),
                      ),
                      child: Row(
                        children: [
                          SvgPicture.asset(
                            "assets/icons/Notification.svg",
                            colorFilter: ColorFilter.mode(
                              Theme.of(context).iconTheme.color!,
                              BlendMode.srcIn,
                            ),
                          ),
                          const SizedBox(width: defaultPadding),
                          Text(
                            "Notifications",
                            style: Theme.of(context)
                                .textTheme
                                .titleMedium!
                                .copyWith(fontWeight: FontWeight.w500),
                          ),
                          const Spacer(),
                          CupertinoSwitch(
                            activeColor: primaryColor,
                            onChanged: (value) {},
                            value: false,
                          ),
                        ],
                      ),
                    ),
                    const Spacer(),
                    ElevatedButton(
                      onPressed: () {
                        Navigator.pushNamed(
                            context, preferredLanuageScreenRoute);
                      },
                      child: const Text("Next"),
                    ),
                    const SizedBox(height: defaultPadding),
                  ],
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}
