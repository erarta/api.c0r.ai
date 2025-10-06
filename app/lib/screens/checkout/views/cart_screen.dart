import 'package:flutter/material.dart';
import 'package:modera/components/product/secondary_product_card.dart';
import 'package:modera/models/product_model.dart';
import 'package:modera/route/screen_export.dart';
import 'package:modera/screens/order/views/components/order_summary_card.dart';

import '../../../constants.dart';
import 'components/coupon_code.dart';

class CartScreen extends StatelessWidget {
  const CartScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
        child: CustomScrollView(
          slivers: [
            SliverToBoxAdapter(
              child: Text(
                "Review your order",
                style: Theme.of(context).textTheme.titleSmall,
              ),
            ),
            // While loading use 👇
            // const ReviewYourItemsSkelton(),
            SliverPadding(
              padding: const EdgeInsets.symmetric(vertical: defaultPadding),
              sliver: SliverList(
                delegate: SliverChildBuilderDelegate(
                  (context, index) => Padding(
                    padding: const EdgeInsets.only(bottom: defaultPadding),
                    child: SecondaryProductCard(
                      image: demoPopularProducts[index].image,
                      brandName: demoPopularProducts[index].brandName,
                      title: demoPopularProducts[index].title,
                      price: demoPopularProducts[index].price,
                      priceAfetDiscount:
                          demoPopularProducts[index].priceAfetDiscount,
                      style: ElevatedButton.styleFrom(
                        maximumSize: const Size(double.infinity, 80),
                        padding: EdgeInsets.zero,
                      ),
                    ),
                  ),
                  childCount: 3,
                ),
              ),
            ),
            const SliverToBoxAdapter(
              child: CouponCode(),
            ),

            const SliverPadding(
              padding: EdgeInsets.symmetric(vertical: defaultPadding * 1.5),
              sliver: SliverToBoxAdapter(
                child: OrderSummaryCard(
                  subTotal: 169.0,
                  discount: 10,
                  totalWithVat: 185,
                  vat: 5,
                ),
              ),
            ),
            SliverPadding(
              padding: const EdgeInsets.symmetric(vertical: defaultPadding),
              sliver: SliverToBoxAdapter(
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.pushNamed(context, paymentMethodScreenRoute);
                  },
                  child: const Text("Continue"),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
