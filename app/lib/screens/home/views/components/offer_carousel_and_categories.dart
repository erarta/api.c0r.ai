import 'package:flutter/material.dart';

import '../../../../constants.dart';
import 'calendar_chips.dart';
import 'offers_carousel.dart';

class OffersCarouselAndCategories extends StatelessWidget {
  const OffersCarouselAndCategories({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // While loading use 👇
        // const OffersSkelton(),
        const OffersCarousel(),
        const SizedBox(height: defaultPadding / 2),
        Padding(
          padding: const EdgeInsets.all(defaultPadding),
          child: Text(
            "Calendar",
            style: Theme.of(context).textTheme.titleSmall,
          ),
        ),
        const CalendarChips(),
      ],
    );
  }
}
