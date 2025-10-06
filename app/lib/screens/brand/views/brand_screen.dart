import 'package:flutter/material.dart';
import 'package:modera/components/product/product_card.dart';
import 'package:modera/components/shopping_bag.dart';
import 'package:modera/constants.dart';
import 'package:modera/models/product_model.dart';
import 'package:modera/route/screen_export.dart';

import 'components/brand_info.dart';
import 'components/brand_search_form.dart';

class BrandScreen extends StatelessWidget {
  const BrandScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
          child: CustomScrollView(
            slivers: [
              SliverAppBar(
                floating: true,
                title: const Text("Lipsy london"),
                actions: [
                  IconButton(
                    onPressed: () {},
                    icon: const ShoppingBag(),
                  ),
                ],
              ),
              SliverToBoxAdapter(
                child: BrandInfo(
                  image: Theme.of(context).brightness == Brightness.dark
                      ? "https://i.imgur.com/l10iLZw.png"
                      : "https://i.imgur.com/KuZFgrs.png",
                  description:
                      "Want the hottest trends right now? Lipsy has all the styles you need to create that glamorous, sexy & sophisticated you!",
                ),
              ),
              const SliverToBoxAdapter(
                child: BrandSearchForm(),
              ),
              SliverPadding(
                padding:
                    const EdgeInsets.symmetric(vertical: defaultPadding * 1.5),
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
                        priceAfetDiscount:
                            demoPopularProducts[index].priceAfetDiscount,
                        dicountpercent:
                            demoPopularProducts[index].dicountpercent,
                        press: () {
                          Navigator.pushNamed(
                              context, productDetailsScreenRoute);
                        },
                      );
                    },
                    childCount: demoPopularProducts.length,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
