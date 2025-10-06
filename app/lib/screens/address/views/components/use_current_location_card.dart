import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../../../../constants.dart';

class UseCurrentLocationCard extends StatelessWidget {
  const UseCurrentLocationCard({
    super.key,
    required this.press,
  });

  final VoidCallback press;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: press,
      borderRadius:
          const BorderRadius.all(Radius.circular(defaultBorderRadious)),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: defaultPadding / 2),
        decoration: BoxDecoration(
          borderRadius:
              const BorderRadius.all(Radius.circular(defaultBorderRadious)),
          border: Border.all(color: Theme.of(context).dividerColor),
        ),
        child: ListTile(
          leading: CircleAvatar(
            radius: 24,
            backgroundColor: primaryColor,
            child: SvgPicture.asset(
              "assets/icons/Mylocation.svg",
              colorFilter:
                  const ColorFilter.mode(Colors.white, BlendMode.srcIn),
            ),
          ),
          title: Text(
            "Use my current location",
            style: Theme.of(context).textTheme.titleSmall,
          ),
          subtitle: Padding(
            padding: const EdgeInsets.only(top: defaultPadding / 2),
            child: Text(
              "John Nowakowska, Zabiniec",
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ),
          trailing: SvgPicture.asset(
            "assets/icons/miniRight.svg",
            colorFilter: ColorFilter.mode(
                Theme.of(context).dividerColor, BlendMode.srcIn),
          ),
        ),
      ),
    );
  }
}
