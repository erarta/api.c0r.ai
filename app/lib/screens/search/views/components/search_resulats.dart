import 'package:flutter/material.dart';
import 'package:modera/components/product/product_card.dart';
import 'package:modera/models/product_model.dart';
import 'package:modera/route/screen_export.dart';

import '../../../../constants.dart';

class SearchResulats extends StatelessWidget {
  const SearchResulats({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return SliverPadding(
      padding: const EdgeInsets.symmetric(
          horizontal: defaultPadding, vertical: defaultPadding),
      sliver: SliverGrid(
        gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
          maxCrossAxisExtent: 200.0,
          mainAxisSpacing: defaultPadding,
          crossAxisSpacing: defaultPadding,
          childAspectRatio: 0.66,
        ),
        delegate: SliverChildBuilderDelegate(
          (BuildContext context, int index) {
            return ProductCard(
              image: demoPopularProducts[index].image,
              brandName: demoPopularProducts[index].brandName,
              title: demoPopularProducts[index].title,
              price: demoPopularProducts[index].price,
              priceAfetDiscount: demoPopularProducts[index].priceAfetDiscount,
              dicountpercent: demoPopularProducts[index].dicountpercent,
              press: () {
                Navigator.pushNamed(context, productDetailsScreenRoute);
              },
            );
          },
          childCount: demoPopularProducts.length,
        ),
      ),
    );
  }
}
