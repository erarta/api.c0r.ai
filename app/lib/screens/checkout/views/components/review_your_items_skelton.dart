import 'package:flutter/material.dart';

import '../../../../components/skleton/product/secondary_product_skelton.dart';
import '../../../../constants.dart';

class ReviewYourItemsSkelton extends StatelessWidget {
  const ReviewYourItemsSkelton({
    super.key,
    this.count = 3,
  });

  final int count;

  @override
  Widget build(BuildContext context) {
    return SliverPadding(
      padding: const EdgeInsets.symmetric(vertical: defaultPadding),
      sliver: SliverList(
        delegate: SliverChildBuilderDelegate(
          (context, index) => const SizedBox(
            height: 80,
            child: SeconderyProductSkelton(isSmall: true),
          ),
          childCount: count,
        ),
      ),
    );
  }
}
