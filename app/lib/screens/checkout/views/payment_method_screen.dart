import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:modera/constants.dart';

import 'components/pay_with_card.dart';
import 'components/pay_with_cash.dart';
import 'components/pay_with_credit.dart';
import 'components/payment_method_button.dart';

class PaymentMethodScreen extends StatefulWidget {
  const PaymentMethodScreen({super.key});

  @override
  State<PaymentMethodScreen> createState() => _PaymentMethodScreenState();
}

class _PaymentMethodScreenState extends State<PaymentMethodScreen> {
  int _selectedMethodIndex = 0;
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Payment method"),
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
      body: Column(
        children: [
          SingleChildScrollView(
            padding: const EdgeInsets.symmetric(vertical: defaultPadding),
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: defaultPadding),
                  child: PayentMethodButton(
                    svgSrc: "assets/icons/card.svg",
                    title: "Pay with card",
                    isActive: _selectedMethodIndex == 0,
                    press: () {
                      setState(() {
                        _selectedMethodIndex = 0;
                      });
                    },
                  ),
                ),
                PayentMethodButton(
                  svgSrc: "assets/icons/Cash.svg",
                  title: "Pay with cash",
                  isActive: _selectedMethodIndex == 1,
                  press: () {
                    setState(() {
                      _selectedMethodIndex = 1;
                    });
                  },
                ),
                Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: defaultPadding),
                  child: PayentMethodButton(
                    svgSrc: "assets/icons/card.svg",
                    title: "Use Credit",
                    isActive: _selectedMethodIndex == 2,
                    press: () {
                      setState(() {
                        _selectedMethodIndex = 2;
                      });
                    },
                  ),
                ),
              ],
            ),
          ),
          if (_selectedMethodIndex == 0) const PayWithCard(),
          if (_selectedMethodIndex == 1) const PayWithCash(),
          if (_selectedMethodIndex == 2)
            const PayWithCredit(isInsufficientBalance: true),
        ],
      ),
    );
  }
}
