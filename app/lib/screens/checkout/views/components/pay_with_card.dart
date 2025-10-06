import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:modera/components/card_info.dart';
import 'package:modera/route/screen_export.dart';

import '../../../../constants.dart';

class PayWithCard extends StatefulWidget {
  const PayWithCard({
    super.key,
  });

  @override
  State<PayWithCard> createState() => _PayWithCardState();
}

class _PayWithCardState extends State<PayWithCard> {
  int _selectedCardIndex = 0;
  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(defaultPadding),
              child: Column(
                children: [
                  OutlinedButton.icon(
                    onPressed: () {
                      Navigator.pushNamed(context, addNewCardScreenRoute);
                    },
                    icon: SvgPicture.asset(
                      "assets/icons/Newcard.svg",
                      colorFilter: ColorFilter.mode(
                        Theme.of(context).iconTheme.color!,
                        BlendMode.srcIn,
                      ),
                    ),
                    label: Text(
                      "Add new card",
                      style: TextStyle(
                          color: Theme.of(context).textTheme.bodyLarge!.color),
                    ),
                  ),
                  const SizedBox(height: defaultPadding * 1.5),
                  ...List.generate(
                    demoCards.length,
                    (index) => Padding(
                      padding: const EdgeInsets.only(bottom: defaultPadding),
                      child: CardInfo(
                        press: () {
                          setState(() {
                            _selectedCardIndex = index;
                          });
                        },
                        last4Digits: demoCards[index].last4Digit,
                        name: demoCards[index].name,
                        expiryDate: demoCards[index].expiryDate,
                        bgColor: demoCards[index].bgColor ?? primaryColor,
                        isSelected: _selectedCardIndex == index,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(
                  horizontal: defaultPadding, vertical: defaultPadding / 2),
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pushNamed(context, thanksForOrderScreenRoute);
                },
                child: const Text("Confirm"),
              ),
            ),
          )
        ],
      ),
    );
  }
}

// For demo perpose
class DemoCard {
  final String last4Digit, name, expiryDate;
  final Color? bgColor;

  DemoCard(
      {required this.last4Digit,
      required this.name,
      required this.expiryDate,
      this.bgColor});
}

List<DemoCard> demoCards = [
  DemoCard(
    last4Digit: "1234",
    name: "The Flutter Way",
    expiryDate: "09/24",
  ),
  DemoCard(
    last4Digit: "1234",
    name: "The Flutter Way",
    expiryDate: "09/24",
    bgColor: const Color(0xFFEB9486),
  ),
  DemoCard(
    last4Digit: "1234",
    name: "The Flutter Way",
    expiryDate: "09/24",
    bgColor: const Color(0xFFEABF91),
  ),
];
