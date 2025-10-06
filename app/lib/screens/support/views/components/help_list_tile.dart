import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../../../../constants.dart';

class HelpListTile extends StatelessWidget {
  const HelpListTile({
    super.key,
    required this.svgSrc,
    required this.title,
    required this.subtitle,
    required this.press,
  });

  final String svgSrc, title, subtitle;
  final VoidCallback press;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      onTap: press,
      leading: CircleAvatar(
        radius: 28,
        backgroundColor:
            Theme.of(context).textTheme.bodyLarge!.color!.withOpacity(0.05),
        child: SvgPicture.asset(
          svgSrc,
          height: 24,
          color: Theme.of(context).iconTheme.color,
        ),
      ),
      title: Text(
        title,
        style: const TextStyle(fontWeight: FontWeight.w600),
      ),
      subtitle: Padding(
        padding: const EdgeInsets.only(top: defaultPadding / 4),
        child: Text(subtitle),
      ),
    );
  }
}
