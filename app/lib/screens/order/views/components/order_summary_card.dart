import 'package:flutter/material.dart';

import '../../../../constants.dart';

class OrderSummaryCard extends StatelessWidget {
  const OrderSummaryCard({
    super.key,
    required this.subTotal,
    this.shippingFee = 0,
    required this.totalWithVat,
    required this.vat,
    this.discount,
  });
  final double subTotal, shippingFee, totalWithVat, vat;
  final double? discount;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(defaultPadding),
      decoration: BoxDecoration(
        borderRadius:
            const BorderRadius.all(Radius.circular(defaultBorderRadious)),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Order Summary",
            style: Theme.of(context).textTheme.titleSmall,
          ),
          const SizedBox(height: defaultPadding / 2),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: defaultPadding / 2),
            child: OrderSummaryText(
              leadingText: "Subtotal",
              trilingText: "\$$subTotal",
            ),
          ),
          OrderSummaryText(
            leadingText: "Shipping Fee",
            trilingText: shippingFee == 0 ? "Free" : "\$$shippingFee",
            trilingTextColor: shippingFee == 0 ? successColor : null,
          ),
          if (discount != null) const SizedBox(height: defaultPadding / 2),
          if (discount != null)
            OrderSummaryText(
                leadingText: "Discount", trilingText: "\$$discount"),
          const Divider(height: defaultPadding * 2),
          OrderSummaryText(
            leadingText: "Total (Include of VAT)",
            trilingText: "\$$totalWithVat",
          ),
          const SizedBox(height: defaultPadding / 2),
          OrderSummaryText(
            leadingText: "Estimated VAT",
            trilingText: "\$$vat",
          ),
        ],
      ),
    );
  }
}

class OrderSummaryText extends StatelessWidget {
  const OrderSummaryText({
    super.key,
    required this.leadingText,
    required this.trilingText,
    this.trilingTextColor,
  });

  final String leadingText, trilingText;
  final Color? trilingTextColor;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Text(leadingText),
        const Spacer(),
        Text(
          trilingText,
          style: Theme.of(context)
              .textTheme
              .titleSmall!
              .copyWith(color: trilingTextColor),
        ),
      ],
    );
  }
}
