import 'package:flutter/material.dart';
import 'package:modera/components/order_process.dart';
import 'package:modera/components/order_status_card.dart';
import 'package:modera/components/product/secondary_product_card.dart';
import 'package:modera/constants.dart';
import 'package:modera/models/product_model.dart';
import 'package:modera/route/screen_export.dart';
import 'package:modera/screens/profile/views/components/profile_menu_item_list_tile.dart';

import 'components/help_line.dart';
import 'components/order_summary_card.dart';

class OrderDetailsScreen extends StatelessWidget {
  const OrderDetailsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Order detail"),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Padding(
                padding: EdgeInsets.all(defaultPadding),
                child: OrderStatusCard(
                  orderId: "FDS6398220",
                  placedOn: "Jun 10, 2021",
                  orderStatus: OrderProcessStatus.done,
                  processingStatus: OrderProcessStatus.processing,
                  packedStatus: OrderProcessStatus.notDoneYeat,
                  shippedStatus: OrderProcessStatus.notDoneYeat,
                  deliveredStatus: OrderProcessStatus.notDoneYeat,
                ),
              ),
              const SizedBox(height: defaultPadding / 2),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            "Delivery address",
                            style: Theme.of(context).textTheme.titleSmall,
                          ),
                          const SizedBox(height: defaultPadding / 2),
                          const Text("Zabiniec 12/222, 31-215 \nCracow, Poland")
                        ],
                      ),
                    ),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          Text(
                            "Estimated time",
                            style: Theme.of(context).textTheme.titleSmall,
                          ),
                          const SizedBox(height: defaultPadding / 2),
                          const Text(
                            "Today \n9 AM to 10 AM",
                            textAlign: TextAlign.end,
                          )
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: defaultPadding / 2),
              Padding(
                padding: const EdgeInsets.all(defaultPadding),
                child: Text(
                  "Products",
                  style: Theme.of(context).textTheme.titleSmall,
                ),
              ),
              ...List.generate(
                2,
                (index) => Padding(
                  padding: const EdgeInsets.only(
                      bottom: defaultPadding,
                      left: defaultPadding,
                      right: defaultPadding),
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
              ),
              const SizedBox(height: defaultPadding / 2),
              const Divider(height: 1),
              ProfileMenuListTile(
                svgSrc: "assets/icons/Delivery.svg",
                text: "View shipment",
                press: () {},
              ),
              const Padding(
                padding: EdgeInsets.all(defaultPadding),
                child: OrderSummaryCard(
                  subTotal: 169.0,
                  discount: 10,
                  totalWithVat: 185,
                  vat: 5,
                ),
              ),
              const Padding(
                padding: EdgeInsets.symmetric(vertical: defaultPadding / 2),
                child: HelpLine(number: "+02 9629 4884"),
              ),
              Padding(
                padding: const EdgeInsets.all(defaultPadding),
                child: OutlinedButton(
                  onPressed: () {
                    Navigator.pushNamed(context, cancleOrderScreenRoute);
                  },
                  child: Text(
                    "Cancel order",
                    style: TextStyle(
                        color: Theme.of(context).textTheme.bodyLarge!.color!),
                  ),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
