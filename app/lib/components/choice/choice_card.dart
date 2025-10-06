import 'package:flutter/material.dart';
import 'package:modera/components/check_mark.dart';
import 'package:modera/constants.dart';

class ChoiceCard extends StatelessWidget {
  const ChoiceCard({
    super.key,
    required this.title,
    this.isActive = false,
    required this.onTap,
  });

  final String title;
  final bool isActive;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: isActive ? primaryColor : Colors.transparent,
        borderRadius: const BorderRadius.all(Radius.circular(defaultBorderRadious)),
        border: Border.all(
          width: 1.5,
          color: isActive
              ? Colors.white.withOpacity(0.25)
              : Theme.of(context).textTheme.bodyLarge!.color!.withOpacity(0.10),
        ),
      ),
      child: ListTile(
        onTap: onTap,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(defaultBorderRadious)),
        ),
        title: Text(title, style: TextStyle(color: isActive ? Colors.white : null)),
        trailing: Visibility(
          visible: isActive,
          child: const CheckMark(activeColor: Colors.white, iconColor: primaryColor),
        ),
      ),
    );
  }
}


