import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:modera/components/order_process.dart';
import 'package:modera/components/order_status_card.dart';
import 'package:modera/components/product/secondary_product_card.dart';
import 'package:modera/models/product_model.dart';

import '../../../constants.dart';

class CancleOrderScreen extends StatelessWidget {
  const CancleOrderScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Cancle order"),
        actions: [
          IconButton(
            onPressed: () {},
            icon: SvgPicture.asset(
              "assets/icons/info.svg",
              colorFilter: ColorFilter.mode(
                Theme.of(context).iconTheme.color!,
                BlendMode.srcIn,
              ),
            ),
          )
        ],
      ),
      body: SingleChildScrollView(
        child: SafeArea(
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.all(defaultPadding),
                child: OrderStatusCard(
                  orderId: "FDS6398220",
                  placedOn: "Jun 10, 2021",
                  orderStatus: OrderProcessStatus.done,
                  processingStatus: OrderProcessStatus.done,
                  packedStatus: OrderProcessStatus.done,
                  shippedStatus: OrderProcessStatus.processing,
                  deliveredStatus: OrderProcessStatus.notDoneYeat,
                  products: List.generate(
                    2,
                    (index) => Padding(
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
                  ),
                ),
              ),
              const SizedBox(height: defaultPadding * 0.5),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding:
                        const EdgeInsets.symmetric(horizontal: defaultPadding),
                    child: Text(
                      "What is the biggest reason for your wish to cancel?",
                      style: Theme.of(context).textTheme.titleMedium!.copyWith(
                          color: Theme.of(context).textTheme.bodyMedium!.color),
                    ),
                  ),
                  CheckboxListTile(
                    activeColor: primaryColor,
                    onChanged: (value) {},
                    value: false,
                    controlAffinity: ListTileControlAffinity.leading,
                    title: const Text("It’s too costly."),
                  ),
                  CheckboxListTile(
                    activeColor: primaryColor,
                    onChanged: (value) {},
                    value: false,
                    controlAffinity: ListTileControlAffinity.leading,
                    title: const Text(
                        "I found another product that fulfills my need."),
                  ),
                  CheckboxListTile(
                    activeColor: primaryColor,
                    onChanged: (value) {},
                    value: false,
                    controlAffinity: ListTileControlAffinity.leading,
                    title: const Text("I don’t use it enough."),
                  ),
                ],
              ),
              CheckboxListTile(
                activeColor: primaryColor,
                onChanged: (value) {},
                value: false,
                controlAffinity: ListTileControlAffinity.leading,
                title: const Text("Other"),
              ),
              Padding(
                padding: const EdgeInsets.all(defaultPadding),
                child: ElevatedButton(
                  onPressed: () {},
                  style: ElevatedButton.styleFrom(backgroundColor: errorColor),
                  child: const Text("Cancle"),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
