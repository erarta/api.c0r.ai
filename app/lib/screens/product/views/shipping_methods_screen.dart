import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:modera/constants.dart';

import 'components/express_shipping_method_card.dart';
import 'components/shipping_method_card.dart';
import 'components/standard_shopping_method_card.dart';

class ShippingMethodsScreen extends StatelessWidget {
  const ShippingMethodsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            const SizedBox(height: defaultPadding),
            Padding(
              padding:
                  const EdgeInsets.symmetric(horizontal: defaultPadding / 2),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const BackButton(),
                  Text(
                    "Shipping methods",
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                  IconButton(
                    onPressed: () {},
                    icon: SvgPicture.asset(
                      "assets/icons/Danger Circle.svg",
                      color: Theme.of(context).iconTheme.color,
                    ),
                  ),
                ],
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(defaultPadding),
                child: Column(
                  children: [
                    const StandardShippingMethodCard(),
                    const SizedBox(height: defaultPadding),
                    const ExpressShippingMethodCard(),
                    Padding(
                      padding:
                          const EdgeInsets.symmetric(vertical: defaultPadding),
                      child: ShippingMethodCard(
                        title: "Rush",
                        price: 21.95,
                        subtitle: "Arrives in 1-2 business days",
                        press: () {},
                      ),
                    ),
                    ShippingMethodCard(
                      title: "Truck",
                      price: 102.50,
                      subtitle: "Arrives in 2-4 weeks once shipped",
                      press: () {},
                    ),
                    const SizedBox(height: defaultPadding),
                    const Text(
                      "Rush shipping may not be available for all orders depending on fulfillment location.",
                    ),
                    Padding(
                      padding: const EdgeInsets.symmetric(
                          vertical: defaultPadding / 2),
                      child: Text.rich(
                        TextSpan(
                          text: "Shipping outside of the US? See our ",
                          children: [
                            TextSpan(
                              text: "International shipping rates.",
                              recognizer: TapGestureRecognizer()
                                ..onTap = () {
                                  // Navigate to s hipping rates page
                                },
                              style: const TextStyle(
                                  fontWeight: FontWeight.w500,
                                  color: primaryColor),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const Text(
                      "This item is available for delivery to one of our convenient Collection Points.",
                    ),
                  ],
                ),
              ),
            )
          ],
        ),
      ),
    );
  }
}
