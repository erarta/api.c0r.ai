import 'package:flutter/material.dart';
import 'package:modera/components/order_process.dart';
import 'package:modera/components/order_status_card.dart';
import 'package:modera/components/product/secondary_product_card.dart';
import 'package:modera/models/product_model.dart';

import '../../../constants.dart';

class DelivereOrdersdScreen extends StatelessWidget {
  const DelivereOrdersdScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Delivered"),
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
        child: ListView.separated(
          itemCount: 3,
          // While loading use 👇
          // OrderStatusCardSkelton(),
          itemBuilder: (context, deliveredIndex) => OrderStatusCard(
            orderId: "FDS6398220",
            placedOn: "Jun 10, 2021",
            orderStatus: OrderProcessStatus.done,
            processingStatus: OrderProcessStatus.done,
            packedStatus: OrderProcessStatus.done,
            shippedStatus: OrderProcessStatus.done,
            deliveredStatus: OrderProcessStatus.done,
            products: List.generate(
              2,
              (index) => Padding(
                padding: const EdgeInsets.only(bottom: defaultPadding),
                child: SecondaryProductCard(
                  image: demoPopularProducts[deliveredIndex + index].image,
                  brandName:
                      demoPopularProducts[deliveredIndex + index].brandName,
                  title: demoPopularProducts[deliveredIndex + index].title,
                  price: demoPopularProducts[deliveredIndex + index].price,
                  priceAfetDiscount: demoPopularProducts[deliveredIndex + index]
                      .priceAfetDiscount,
                  style: ElevatedButton.styleFrom(
                    maximumSize: const Size(double.infinity, 80),
                    padding: EdgeInsets.zero,
                  ),
                ),
              ),
            ),
          ),
          separatorBuilder: (context, index) =>
              const SizedBox(height: defaultPadding),
        ),
      ),
    );
  }
}
