import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:modera/components/check_mark.dart';

import '../../../../constants.dart';

class VerificationMethodCard extends StatelessWidget {
  const VerificationMethodCard({
    super.key,
    required this.isActive,
    required this.text,
    required this.svgSrc,
    required this.press,
  });

  final bool isActive;
  final String text, svgSrc;
  final VoidCallback press;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        borderRadius:
            const BorderRadius.all(Radius.circular(defaultBorderRadious)),
        border: Border.all(
          color: isActive
              ? primaryColor
              : Theme.of(context).textTheme.bodyLarge!.color!.withOpacity(0.1),
        ),
      ),
      child: ListTile(
        onTap: press,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.all(Radius.circular(defaultBorderRadious)),
        ),
        minLeadingWidth: 24,
        leading: SvgPicture.asset(
          svgSrc,
          height: 24,
          colorFilter: ColorFilter.mode(
            isActive
                ? primaryColor
                : Theme.of(context).textTheme.bodyLarge!.color!,
            BlendMode.srcIn,
          ),
        ),
        title: Text(text),
        trailing: isActive ? const CheckMark() : null,
      ),
    );
  }
}
