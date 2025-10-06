import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../../../../constants.dart';
import 'rating_sort_dropdown_button.dart';

class SortUserReview extends SliverPersistentHeaderDelegate {
  @override
  Widget build(
      BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
      color: Theme.of(context).scaffoldBackgroundColor,
      child: Row(
        children: [
          Expanded(
            child: Text(
              "User reviews",
              style: Theme.of(context).textTheme.titleSmall,
            ),
          ),
          SvgPicture.asset(
            "assets/icons/Sort.svg",
            color: Theme.of(context).iconTheme.color,
          ),
          const SizedBox(width: defaultPadding / 2),
          RatingSortDropdownButton(
            items: const ['Most useful', 'Recent'],
            value: "Most useful",
            onChanged: (value) {
              // Set the dropdown value
            },
          )
        ],
      ),
    );
  }

  @override
  double get maxExtent => 40;

  @override
  double get minExtent => 40;

  @override
  bool shouldRebuild(covariant SliverPersistentHeaderDelegate oldDelegate) {
    return true;
  }
}
