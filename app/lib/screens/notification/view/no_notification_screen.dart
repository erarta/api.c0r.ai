import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';

import 'components/no_notification.dart';

class NoNotificationScreen extends StatelessWidget {
  const NoNotificationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Notifications"),
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
      body: const SafeArea(child: NoNotification()),
    );
  }
}
