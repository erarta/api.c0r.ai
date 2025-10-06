import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:modera/constants.dart';

import 'components/order_summery.dart';

class ThanksForOrderScreen extends StatelessWidget {
  const ThanksForOrderScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Order"),
        actions: [
          IconButton(
            onPressed: () {},
            icon: SvgPicture.asset(
              "assets/icons/Share.svg",
              colorFilter: ColorFilter.mode(
                Theme.of(context).iconTheme.color!,
                BlendMode.srcIn,
              ),
            ),
          )
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(defaultPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Spacer(),
              Center(
                child: Image.asset(
                  Theme.of(context).brightness == Brightness.dark
                      ? "assets/Illustration/Success_darkTheme.png"
                      : "assets/Illustration/Success_lightTheme.png",
                  width: MediaQuery.of(context).size.width * 0.5,
                ),
              ),
              const SizedBox(height: defaultPadding * 2),
              Text(
                "Thanks for your order",
                style: Theme.of(context).textTheme.titleLarge,
              ),
              Padding(
                padding: const EdgeInsets.symmetric(vertical: defaultPadding),
                child: Text.rich(
                  TextSpan(
                    text: "You’ll receive an email at  ",
                    children: [
                      TextSpan(
                        text: "your.mail@gmail.com",
                        style: TextStyle(
                            color: Theme.of(context).textTheme.bodyLarge!.color,
                            fontWeight: FontWeight.w500),
                      ),
                      const TextSpan(text: "  once your order is confirmed.")
                    ],
                  ),
                ),
              ),
              const Padding(
                padding: EdgeInsets.symmetric(vertical: defaultPadding),
                child: OrderSummary(
                  orderId: "FDS639820",
                  amount: 476.98,
                ),
              ),
              const Spacer(),
              ElevatedButton.icon(
                onPressed: () {},
                icon: SvgPicture.asset(
                  "assets/icons/Trackorder.svg",
                  colorFilter: const ColorFilter.mode(
                    Colors.white,
                    BlendMode.srcIn,
                  ),
                ),
                label: const Text("Track order"),
              )
            ],
          ),
        ),
      ),
    );
  }
}
