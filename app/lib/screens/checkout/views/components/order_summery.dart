import 'package:flutter/material.dart';
import 'package:modera/screens/order/views/components/order_summary_card.dart';

import '../../../../constants.dart';

class OrderSummary extends StatelessWidget {
  const OrderSummary({
    super.key,
    required this.orderId,
    required this.amount,
  });

  final String orderId;
  final double amount;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(defaultPadding),
      decoration: BoxDecoration(
        border: Border.all(color: Theme.of(context).dividerColor),
        borderRadius:
            const BorderRadius.all(Radius.circular(defaultBorderRadious)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Order Summary",
            style: Theme.of(context).textTheme.titleSmall,
          ),
          const SizedBox(height: defaultPadding),
          OrderSummaryText(
            leadingText: "Order number",
            trilingText: "#$orderId",
          ),
          const SizedBox(height: defaultPadding / 2),
          OrderSummaryText(
            leadingText: "Amount paid",
            trilingText: "\$${amount.toStringAsFixed(2)}",
            trilingTextColor: successColor,
          ),
        ],
      ),
    );
  }
}
