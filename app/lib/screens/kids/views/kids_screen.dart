import 'package:flutter/material.dart';
import 'package:modera/components/Banner/L/banner_l_style_1.dart';
import 'package:modera/components/Banner/S/banner_s_style_1.dart';
import 'package:modera/components/Banner/S/banner_s_style_4.dart';
import 'package:modera/components/product/product_card.dart';
import 'package:modera/components/shopping_bag.dart';
import 'package:modera/constants.dart';
import 'package:modera/models/product_model.dart';
import 'package:modera/route/route_constants.dart';
import 'package:modera/screens/search/views/components/search_form.dart';

class KidsScreen extends StatelessWidget {
  const KidsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: CustomScrollView(
          slivers: [
            const SliverAppBar(
              floating: true,
              title: Text("Kids"),
              actions: [
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: defaultPadding),
                  child: ShoppingBag(),
                ),
              ],
            ),
            const SliverPadding(
              padding: EdgeInsets.all(defaultPadding),
              sliver: SliverToBoxAdapter(
                child: SearchForm(),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.only(top: defaultPadding / 2),
              sliver: SliverToBoxAdapter(
                child: BannerLStyle1(
                  image: "https://i.imgur.com/z7noLen.png",
                  title: "FASHION SALE",
                  subtitle: "SPECIAL OFFER",
                  discountPercent: 25,
                  press: () {},
                ),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.only(top: defaultPadding / 4),
              sliver: SliverToBoxAdapter(
                child: Column(
                  children: [
                    BannerSStyle1(
                      image: "https://i.imgur.com/y4SR4Vy.png",
                      title: "New \narrival",
                      subtitle: "SPECIAL OFFER",
                      discountParcent: 50,
                      press: () {},
                    ),
                    const SizedBox(height: defaultPadding / 4),
                    BannerSStyle4(
                      image: "https://i.imgur.com/bmNTJLV.png",
                      title: "Black \nfriday",
                      subtitle: "50% off",
                      bottomText: "Collection".toUpperCase(),
                      press: () {},
                    ),
                  ],
                ),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.symmetric(
                  vertical: defaultPadding * 1.5, horizontal: defaultPadding),
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
                      image: kidsProducts[index].image,
                      brandName: kidsProducts[index].brandName,
                      title: kidsProducts[index].title,
                      price: kidsProducts[index].price,
                      priceAfetDiscount: kidsProducts[index].priceAfetDiscount,
                      dicountpercent: kidsProducts[index].dicountpercent,
                      press: () {
                        Navigator.pushNamed(context, productDetailsScreenRoute);
                      },
                    );
                  },
                  childCount: kidsProducts.length,
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}
