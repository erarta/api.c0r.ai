import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:modera/constants.dart';

import 'components/notification_card.dart';

class NotificationsScreen extends StatelessWidget {
  const NotificationsScreen({super.key});

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
      body: SafeArea(
        // For no notification use
        // NoNotification()
        child: ListView.builder(
          itemCount: 10,
          itemBuilder: (context, index) => NotificationCard(
            title: "Molestie libero neque sem cras enim, amet.",
            svgSrc: index.isEven
                ? "assets/icons/Discount.svg"
                : "assets/icons/diamond.svg",
            time: "2 min ago",
            iconBgColor: index.isEven ? const Color(0xFFF3B923) : primaryColor,
            isRead: index > 2,
          ),
        ),
      ),
    );
  }
}
