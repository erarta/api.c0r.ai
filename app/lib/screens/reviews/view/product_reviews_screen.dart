import 'package:flutter/material.dart';
import 'package:modera/components/review_card.dart';
import 'package:modera/constants.dart';
import 'package:modera/screens/product/views/components/product_list_tile.dart';
import 'package:modera/route/screen_export.dart';

import 'components/sort_user_review.dart';
import 'components/user_review_card.dart';

class ProductReviewsScreen extends StatelessWidget {
  const ProductReviewsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            pinned: true,
            title: const Text("Reviews"),
            backgroundColor: Theme.of(context).scaffoldBackgroundColor,
          ),
          const SliverPadding(
            padding: EdgeInsets.symmetric(horizontal: defaultPadding),
            sliver: SliverToBoxAdapter(
              child: ReviewCard(
                rating: 4.3,
                numOfReviews: 120,
                numOfFiveStar: 90,
                numOfFourStar: 20,
                numOfThreeStar: 4,
                numOfTwoStar: 0,
                numOfOneStar: 6,
              ),
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.symmetric(vertical: defaultPadding),
            sliver: ProductListTile(
              title: "Add Review",
              svgSrc: "assets/icons/Chat-add.svg",
              isShowBottomBorder: true,
              press: () {
                Navigator.pushNamed(context, addReviewsScreenRoute);
              },
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
            sliver: SliverPersistentHeader(
              delegate: SortUserReview(),
              pinned: true,
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
            sliver: SliverList(
              delegate: SliverChildBuilderDelegate(
                (context, index) => Padding(
                  padding: const EdgeInsets.only(top: defaultPadding),
                  child: UserReviewCard(
                    rating: 4.2,
                    name: "Arman Rokni",
                    userImage:
                        index.isEven ? null : "https://i.imgur.com/4h34UKX.png",
                    time: "36s",
                    review:
                        "“A cool gray cap in soft cssorduroy. Watch me.' By bussying cottoaaan products from Lindex, you’re  more responsibly.”",
                  ),
                ),
                childCount: 7,
              ),
            ),
          ),
          const SliverToBoxAdapter(
              child: SizedBox(height: defaultPadding * 1.5)),
        ],
      ),
    );
  }
}
