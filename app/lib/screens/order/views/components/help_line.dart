import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../../../../constants.dart';

class HelpLine extends StatelessWidget {
  const HelpLine({
    super.key,
    required this.number,
  });
  final String number;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(
        "Need help with anything?",
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w500,
          color: Theme.of(context).textTheme.bodyMedium!.color,
        ),
      ),
      subtitle: Padding(
        padding: const EdgeInsets.only(top: defaultPadding / 2),
        child: Text(
          "Call $number",
          style: Theme.of(context).textTheme.titleSmall,
        ),
      ),
      trailing: CircleAvatar(
        radius: 24,
        backgroundColor: primaryColor,
        child: SvgPicture.asset(
          "assets/icons/Call.svg",
          height: 24,
          width: 24,
        ),
      ),
    );
  }
}
