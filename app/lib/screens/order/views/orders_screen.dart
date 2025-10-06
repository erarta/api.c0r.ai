import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/screen_export.dart';

class OrdersScreen extends StatelessWidget {
  const OrdersScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Orders"),
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(defaultPadding),
            child: Text(
              "Orders history",
              style: Theme.of(context).textTheme.titleSmall,
            ),
          ),
          OrderHistoryListTile(
            svgSrc: "assets/icons/Payonline.svg",
            title: "Awaiting Payment",
            counterColor: warningColor,
            numOfItem: 0,
            press: () {},
          ),
          OrderHistoryListTile(
            svgSrc: "assets/icons/Product.svg",
            title: "Processing",
            numOfItem: 1,
            press: () {
              Navigator.pushNamed(context, orderProcessingScreenRoute);
            },
          ),
          OrderHistoryListTile(
            svgSrc: "assets/icons/Delivery.svg",
            title: "Delivered",
            numOfItem: 5,
            press: () {
              Navigator.pushNamed(context, deliveredOrdersScreenRoute);
            },
          ),
          OrderHistoryListTile(
            svgSrc: "assets/icons/Return.svg",
            title: "Returned",
            numOfItem: 2,
            press: () {},
          ),
          OrderHistoryListTile(
            svgSrc: "assets/icons/Close-Circle.svg",
            title: "Canceled",
            numOfItem: 2,
            counterColor: errorColor,
            press: () {
              Navigator.pushNamed(context, cancledOrdersScreenRoute);
            },
            isShowDivider: false,
          ),
        ],
      ),
    );
  }
}

class OrderHistoryListTile extends StatelessWidget {
  const OrderHistoryListTile({
    super.key,
    required this.svgSrc,
    required this.title,
    this.counterColor = primaryColor,
    required this.numOfItem,
    required this.press,
    this.isShowDivider = true,
  });

  final String svgSrc, title;
  final Color counterColor;
  final int numOfItem;
  final VoidCallback press;
  final bool isShowDivider;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ListTile(
          onTap: press,
          minLeadingWidth: 24,
          leading: SvgPicture.asset(
            svgSrc,
            height: 24,
            width: 24,
            colorFilter: ColorFilter.mode(
              Theme.of(context).iconTheme.color!,
              BlendMode.srcIn,
            ),
          ),
          title: Text(title),
          trailing: SizedBox(
            width: 56,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  height: 20,
                  width: 28,
                  decoration: BoxDecoration(
                    color: counterColor,
                    borderRadius: const BorderRadius.all(Radius.circular(30)),
                  ),
                  child: Center(
                    child: Text(
                      numOfItem.toString(),
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontWeight: FontWeight.w500,
                        color: Colors.white,
                        fontSize: 12,
                        height: 1,
                      ),
                    ),
                  ),
                ),
                SvgPicture.asset(
                  "assets/icons/miniRight.svg",
                  colorFilter: ColorFilter.mode(
                    Theme.of(context).iconTheme.color!.withOpacity(0.4),
                    BlendMode.srcIn,
                  ),
                ),
              ],
            ),
          ),
        ),
        if (isShowDivider) const Divider(),
      ],
    );
  }
}
