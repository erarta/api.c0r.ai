import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../../../../constants.dart';

class UseAvailableCredit extends StatelessWidget {
  const UseAvailableCredit({
    super.key,
    required this.availableBalance,
    required this.onChanged,
    required this.value,
  });

  final double availableBalance;
  final ValueChanged<bool> onChanged;
  final bool value;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(defaultPadding),
      decoration: BoxDecoration(
        border: Border.all(color: Theme.of(context).dividerColor),
        borderRadius:
            const BorderRadius.all(Radius.circular(defaultBorderRadious)),
      ),
      child: Column(
        children: [
          ListTile(
            contentPadding: EdgeInsets.zero,
            minVerticalPadding: 0,
            minLeadingWidth: 24,
            leading: SvgPicture.asset(
              "assets/icons/card.svg",
              height: 24,
              width: 24,
              colorFilter: ColorFilter.mode(
                Theme.of(context).iconTheme.color!,
                BlendMode.srcIn,
              ),
            ),
            title: const Text("Use Credit for this purchase"),
            trailing: CupertinoSwitch(
              value: value,
              activeColor: primaryColor,
              onChanged: onChanged,
            ),
          ),
          const SizedBox(height: defaultPadding / 2),
          Container(
            padding: const EdgeInsets.all(defaultPadding),
            decoration: BoxDecoration(
              color: Theme.of(context).dividerColor,
              borderRadius:
                  const BorderRadius.all(Radius.circular(defaultBorderRadious)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("Available Balance:"),
                Text(
                  "\$$availableBalance",
                  style: Theme.of(context).textTheme.titleSmall,
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}
