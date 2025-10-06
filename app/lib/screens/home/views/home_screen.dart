import 'package:flutter/material.dart';
import 'package:modera/components/Banner/L/banner_l_style_1.dart';
import 'package:modera/components/Banner/S/banner_s_style_1.dart';
import 'package:modera/components/Banner/S/banner_s_style_4.dart';
import 'package:modera/components/Banner/S/banner_s_style_5.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/screen_export.dart';

import 'components/best_sellers.dart';
import 'components/flash_sale.dart';
import 'components/most_popular.dart';
import 'components/offer_carousel_and_categories.dart';
import 'components/popular_products.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            const SliverToBoxAdapter(child: OffersCarouselAndCategories()),
            const SliverToBoxAdapter(child: PopularProducts()),
            const SliverPadding(
              padding: EdgeInsets.symmetric(vertical: defaultPadding * 1.5),
              sliver: SliverToBoxAdapter(child: FlashSale()),
            ),
            SliverToBoxAdapter(
              child: Column(
                children: [
                  // While loading use 👇
                  // const BannerMSkelton(),‚
                  BannerSStyle1(
                    title: "New \narrival",
                    subtitle: "SPECIAL OFFER",
                    discountParcent: 50,
                    press: () {
                      Navigator.pushNamed(context, onSaleScreenRoute);
                    },
                  ),
                  const SizedBox(height: defaultPadding / 4),
                  // While loading use 👇
                  //  const BannerMSkelton(),
                  BannerSStyle4(
                    title: "SUMMER \nSALE",
                    subtitle: "SPECIAL OFFER",
                    bottomText: "UP TO 80% OFF",
                    press: () {
                      Navigator.pushNamed(context, onSaleScreenRoute);
                    },
                  ),
                  const SizedBox(height: defaultPadding / 4),
                  // While loading use 👇
                  //  const BannerMSkelton(),
                  BannerSStyle4(
                    image: "https://i.imgur.com/dBrsD0M.png",
                    title: "Black \nfriday",
                    subtitle: "50% off",
                    bottomText: "Collection".toUpperCase(),
                    press: () {
                      Navigator.pushNamed(context, onSaleScreenRoute);
                    },
                  ),
                ],
              ),
            ),
            const SliverToBoxAdapter(child: BestSellers()),
            const SliverToBoxAdapter(child: MostPopular()),
            SliverToBoxAdapter(
              child: Column(
                children: [
                  const SizedBox(height: defaultPadding * 1.5),
                  // While loading use 👇
                  // const BannerLSkelton(),
                  BannerLStyle1(
                    title: "Summer \nSale",
                    subtitle: "SPECIAL OFFER",
                    discountPercent: 50,
                    press: () {
                      Navigator.pushNamed(context, onSaleScreenRoute);
                    },
                  ),
                  const SizedBox(height: defaultPadding / 4),
                  // While loading use 👇
                  // const BannerSSkelton(),
                  BannerSStyle5(
                    title: "Black \nfriday",
                    subtitle: "50% Off",
                    bottomText: "Collection".toUpperCase(),
                    press: () {
                      Navigator.pushNamed(context, onSaleScreenRoute);
                    },
                  ),
                  const SizedBox(height: defaultPadding / 4),
                  // While loading use 👇
                  // const BannerSSkelton(),
                  BannerSStyle5(
                    image: "https://i.imgur.com/2443sJb.png",
                    title: "Grab \nyours now",
                    subtitle: "65% Off",
                    press: () {
                      Navigator.pushNamed(context, onSaleScreenRoute);
                    },
                  ),
                ],
              ),
            ),
            const SliverToBoxAdapter(child: BestSellers()),
          ],
        ),
      ),
    );
  }
}
