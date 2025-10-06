import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_svg/svg.dart';
import 'package:modera/constants.dart';
import 'package:modera/screens/payment/views/components/card_input_formatters.dart';

import 'components/payment_card.dart';

class AddNewCardScreen extends StatefulWidget {
  const AddNewCardScreen({super.key});

  @override
  State<AddNewCardScreen> createState() => _AddNewCardScreenState();
}

class _AddNewCardScreenState extends State<AddNewCardScreen> {
  final _formKey = GlobalKey<FormState>();
  TextEditingController numberController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: const BackButton(),
        title: const Text("New card"),
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
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(defaultPadding),
          child: Column(
            children: [
              Expanded(
                child: Form(
                  key: _formKey,
                  child: SingleChildScrollView(
                    child: Column(
                      children: [
                        TextFormField(
                          onSaved: (String? value) {
                            /// Use [getCleanedNumber]
                            // String cardNumber = CardUtils.getCleanedNumber(value!);
                          },
                          keyboardType: TextInputType.number,
                          inputFormatters: [
                            CardNumberInputFormatter(),
                            FilteringTextInputFormatter.digitsOnly,
                            LengthLimitingTextInputFormatter(9),
                          ],
                          controller: numberController,
                          validator: CardUtils.validateCardNum,
                          decoration: InputDecoration(
                            hintText: "Card number",
                            prefixIcon: Padding(
                              padding: const EdgeInsets.symmetric(
                                  vertical: defaultPadding * 0.75),
                              child: SvgPicture.asset(
                                "assets/icons/card.svg",
                                colorFilter: ColorFilter.mode(
                                  Theme.of(context)
                                      .inputDecorationTheme
                                      .hintStyle!
                                      .color!,
                                  BlendMode.srcIn,
                                ),
                              ),
                            ),
                          ),
                        ),
                        Padding(
                          padding: const EdgeInsets.symmetric(
                              vertical: defaultPadding),
                          child: TextFormField(
                            decoration: InputDecoration(
                              hintText: "Full name",
                              prefixIcon: Padding(
                                padding: const EdgeInsets.symmetric(
                                    vertical: defaultPadding * 0.75),
                                child: SvgPicture.asset(
                                  "assets/icons/Profile.svg",
                                  height: 24,
                                  colorFilter: ColorFilter.mode(
                                    Theme.of(context)
                                        .inputDecorationTheme
                                        .hintStyle!
                                        .color!,
                                    BlendMode.srcIn,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                        Row(
                          children: [
                            Expanded(
                              child: TextFormField(
                                onSaved: (String? value) {
                                  // int cvv = int.parse(value!);
                                },
                                validator: CardUtils.validateCVV,
                                keyboardType: TextInputType.number,
                                inputFormatters: [
                                  FilteringTextInputFormatter.digitsOnly,
                                  LengthLimitingTextInputFormatter(4),
                                ],
                                decoration: InputDecoration(
                                  hintText: "CVV",
                                  prefixIcon: Padding(
                                    padding: const EdgeInsets.symmetric(
                                        vertical: defaultPadding * 0.75),
                                    child: SvgPicture.asset(
                                      "assets/icons/CVV.svg",
                                      height: 24,
                                      colorFilter: ColorFilter.mode(
                                        Theme.of(context)
                                            .inputDecorationTheme
                                            .hintStyle!
                                            .color!,
                                        BlendMode.srcIn,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: defaultPadding),
                            Expanded(
                              child: TextFormField(
                                onSaved: (value) {
                                  // List<int> expiryDate =
                                  //     CardUtils.getExpiryDate(value!);
                                  // int month = expiryDate[0];
                                  // int year = expiryDate[1];
                                },
                                validator: CardUtils.validateDate,
                                keyboardType: TextInputType.number,
                                inputFormatters: [
                                  CardMonthInputFormatter(),
                                  FilteringTextInputFormatter.digitsOnly,
                                  LengthLimitingTextInputFormatter(4),
                                ],
                                decoration: InputDecoration(
                                  hintText: "Expiry date",
                                  prefixIcon: Padding(
                                    padding: const EdgeInsets.symmetric(
                                        vertical: defaultPadding * 0.75),
                                    child: SvgPicture.asset(
                                      "assets/icons/Calender.svg",
                                      height: 24,
                                      colorFilter: ColorFilter.mode(
                                        Theme.of(context)
                                            .inputDecorationTheme
                                            .hintStyle!
                                            .color!,
                                        BlendMode.srcIn,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        )
                      ],
                    ),
                  ),
                ),
              ),
              ElevatedButton(
                onPressed: () {},
                child: const Text("Add card"),
              )
            ],
          ),
        ),
      ),
    );
  }
}

class Strings {
  static const String appName = 'Payment Card Demo';
  static const String fieldReq = 'This field is required';
  static const String numberIsInvalid = 'Card is invalid';
  static const String pay = 'Validate';
}
