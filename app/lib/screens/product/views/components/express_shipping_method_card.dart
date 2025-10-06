import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../../../../constants.dart';

class ExpressShippingMethodCard extends StatelessWidget {
  const ExpressShippingMethodCard({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(defaultPadding / 4),
      decoration: const BoxDecoration(
        color: Color(0xFFADDFEF),
        borderRadius: BorderRadius.all(Radius.circular(defaultBorderRadious)),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(defaultPadding),
            decoration: BoxDecoration(
              color: Theme.of(context).scaffoldBackgroundColor,
              borderRadius:
                  const BorderRadius.all(Radius.circular(defaultBorderRadious)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    SvgPicture.asset(
                      "assets/icons/diamond.svg",
                      colorFilter: ColorFilter.mode(
                        Theme.of(context).iconTheme.color!,
                        BlendMode.srcIn,
                      ),
                    ),
                    const SizedBox(width: defaultPadding / 2),
                    Text(
                      "Express",
                      style: Theme.of(context)
                          .textTheme
                          .titleMedium!
                          .copyWith(fontWeight: FontWeight.w500),
                    ),
                    const Spacer(),
                    Text(
                      "\$14.95",
                      style: Theme.of(context).textTheme.titleSmall,
                    ),
                  ],
                ),
                const SizedBox(height: defaultPadding / 2),
                const Text(
                  "Arrives in 2-3 business days",
                  style: TextStyle(fontSize: 12),
                ),
                const SizedBox(height: defaultPadding / 2),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: defaultPadding),
            child: Text(
              "Free with Modera Premier",
              style: Theme.of(context)
                  .textTheme
                  .bodySmall!
                  .copyWith(color: blackColor, fontWeight: FontWeight.w500),
            ),
          ),
        ],
      ),
    );
  }
}
