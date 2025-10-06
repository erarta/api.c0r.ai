import 'package:flutter/material.dart';
import 'package:modera/components/chat_active_dot.dart';
import 'package:modera/components/network_image_with_loader.dart';

class SupportPersonInfo extends StatelessWidget {
  const SupportPersonInfo({
    super.key,
    required this.image,
    required this.name,
    required this.isActive,
    required this.isConnected,
    this.isTyping = false,
  });

  final String image, name;
  final bool isActive, isConnected, isTyping;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Theme.of(context).iconTheme.color!.withOpacity(0.05),
      child: ListTile(
        title: Row(
          children: [
            Text("$name is "),
            if (isConnected && !isTyping) const Text("connected"),
            if (isConnected && isTyping) const Text("typing..."),
          ],
        ),
        minLeadingWidth: 24,
        leading: CircleAvatar(
          radius: 12,
          child: Stack(
            clipBehavior: Clip.none,
            children: [
              NetworkImageWithLoader(
                image,
                radius: 40,
              ),
              if (isActive)
                const Positioned(
                  right: -4,
                  top: -4,
                  child: ChatActiveDot(),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
