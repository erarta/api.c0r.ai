import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../../../../constants.dart';

class StandardShippingMethodCard extends StatelessWidget {
  const StandardShippingMethodCard({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(defaultPadding / 4),
      decoration: const BoxDecoration(
        color: primaryColor,
        borderRadius: BorderRadius.all(
          Radius.circular(defaultBorderRadious),
        ),
      ),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(defaultPadding),
            decoration: BoxDecoration(
              color: Theme.of(context).scaffoldBackgroundColor,
              borderRadius: const BorderRadius.all(
                Radius.circular(defaultBorderRadious),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    SvgPicture.asset(
                      'assets/icons/Standard.svg',
                      color: Theme.of(context).iconTheme.color,
                    ),
                    const SizedBox(width: defaultPadding / 2),
                    Text(
                      "Standard",
                      style: Theme.of(context).textTheme.titleMedium!.copyWith(
                            fontWeight: FontWeight.w500,
                          ),
                    ),
                  ],
                ),
                const SizedBox(height: defaultPadding / 2),
                const Text(
                  "Arrives in 5-8 business days",
                  style: TextStyle(fontSize: 12),
                ),
                const SizedBox(height: defaultPadding),
                DefaultTextStyle(
                  style: Theme.of(context).textTheme.bodySmall!.copyWith(
                      color: Theme.of(context).textTheme.bodyLarge!.color,
                      fontWeight: FontWeight.w500),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text("Order up to \$49.99:"),
                      Text("\$4.95")
                    ],
                  ),
                ),
                const SizedBox(height: defaultPadding / 2),
                DefaultTextStyle(
                  style: Theme.of(context).textTheme.bodySmall!.copyWith(
                      color: Theme.of(context).textTheme.bodyLarge!.color,
                      fontWeight: FontWeight.w500),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text("Orders \$50 and over:"),
                      Text("Free")
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: defaultPadding),
          Text(
            "Free with Modera Premier",
            style: Theme.of(context)
                .textTheme
                .bodySmall!
                .copyWith(color: Colors.white, fontWeight: FontWeight.w500),
          ),
          const SizedBox(height: defaultPadding * 0.75),
        ],
      ),
    );
  }
}
