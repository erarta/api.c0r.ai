import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:modera/components/check_mark.dart';

import '../../../../constants.dart';

class LanguageCard extends StatelessWidget {
  const LanguageCard({
    super.key,
    required this.flag,
    required this.language,
    this.isActive = false,
    required this.press,
  });

  final String flag, language;
  final bool isActive;
  final VoidCallback press;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: isActive ? primaryColor : Colors.transparent,
        borderRadius: const BorderRadius.all(
          Radius.circular(defaultBorderRadious),
        ),
        border: Border.all(
            color: isActive
                ? Colors.transparent
                : Theme.of(context)
                    .textTheme
                    .bodyLarge!
                    .color!
                    .withOpacity(0.1)),
      ),
      child: ListTile(
        onTap: press,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.all(
            Radius.circular(defaultBorderRadious),
          ),
        ),
        minLeadingWidth: 24,
        leading: SvgPicture.asset(
          flag,
          height: 24,
          width: 24,
        ),
        title: Text(
          language,
          style: TextStyle(color: isActive ? Colors.white : null),
        ),
        trailing: Visibility(
          visible: isActive,
          child: const CheckMark(
            activeColor: Colors.white,
            iconColor: primaryColor,
          ),
        ),
      ),
    );
  }
}
