import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:form_field_validator/form_field_validator.dart';
import 'package:modera/constants.dart';

import 'components/use_current_location_card.dart';

class AddNewAddressScreen extends StatelessWidget {
  const AddNewAddressScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("New address"),
      ),
      body: SafeArea(
        child: Form(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(defaultPadding),
            child: Column(
              children: [
                TextFormField(
                  onSaved: (newValue) {},
                  validator:
                      RequiredValidator(errorText: "This field is required")
                          .call,
                  decoration: const InputDecoration(
                    hintText: "Type address title",
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(
                      vertical: defaultPadding * 1.5),
                  child: UseCurrentLocationCard(press: () {}),
                ),
                TextFormField(
                  onSaved: (newValue) {},
                  validator:
                      RequiredValidator(errorText: "This field is required")
                          .call,
                  decoration: InputDecoration(
                    hintText: "Country/Region",
                    prefixIcon: Padding(
                      padding: const EdgeInsets.symmetric(
                          vertical: defaultPadding * 0.74),
                      child: SvgPicture.asset(
                        "assets/icons/Address.svg",
                        height: 24,
                        width: 24,
                        colorFilter: ColorFilter.mode(
                            Theme.of(context)
                                .inputDecorationTheme
                                .hintStyle!
                                .color!,
                            BlendMode.srcIn),
                      ),
                    ),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: defaultPadding),
                  child: TextFormField(
                    onSaved: (newValue) {},
                    validator:
                        RequiredValidator(errorText: "This field is required")
                            .call,
                    decoration: InputDecoration(
                      hintText: "Full name",
                      prefixIcon: Padding(
                        padding: const EdgeInsets.symmetric(
                            vertical: defaultPadding * 0.74),
                        child: SvgPicture.asset(
                          "assets/icons/Profile.svg",
                          height: 24,
                          width: 24,
                          colorFilter: ColorFilter.mode(
                              Theme.of(context)
                                  .inputDecorationTheme
                                  .hintStyle!
                                  .color!,
                              BlendMode.srcIn),
                        ),
                      ),
                    ),
                  ),
                ),
                TextFormField(
                  onSaved: (newValue) {},
                  validator:
                      RequiredValidator(errorText: "This field is required")
                          .call,
                  decoration: const InputDecoration(
                    hintText: "Address line 1",
                  ),
                ),
                const SizedBox(height: defaultPadding),
                TextFormField(
                  onSaved: (newValue) {},
                  decoration: const InputDecoration(
                    hintText: "Address line 2",
                  ),
                ),
                ListTile(
                  contentPadding:
                      const EdgeInsets.symmetric(vertical: defaultPadding),
                  title: const Text("P.O. Box"),
                  trailing: CupertinoSwitch(
                    onChanged: (value) {},
                    value: false,
                    activeColor: primaryColor,
                  ),
                ),
                TextFormField(
                  onSaved: (newValue) {},
                  decoration: const InputDecoration(
                    hintText: "City",
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: defaultPadding),
                  child: TextFormField(
                    onSaved: (newValue) {},
                    decoration: const InputDecoration(
                      hintText: "State",
                    ),
                  ),
                ),
                TextFormField(
                  onSaved: (newValue) {},
                  decoration: const InputDecoration(
                    hintText: "Zip code",
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: defaultPadding),
                  child: TextFormField(
                    keyboardType: TextInputType.phone,
                    decoration: InputDecoration(
                      hintText: "Phone number",
                      prefixIcon: Padding(
                        padding: const EdgeInsets.only(left: defaultPadding),
                        child: SizedBox(
                          width: 72,
                          child: Row(
                            children: [
                              SvgPicture.asset(
                                "assets/icons/Call.svg",
                                height: 24,
                                width: 24,
                                colorFilter: ColorFilter.mode(
                                    Theme.of(context)
                                        .textTheme
                                        .bodyLarge!
                                        .color!,
                                    BlendMode.srcIn),
                              ),
                              Padding(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: defaultPadding / 2),
                                child: Text("+1",
                                    style:
                                        Theme.of(context).textTheme.bodyLarge),
                              ),
                              const SizedBox(
                                height: 24,
                                child: VerticalDivider(
                                  thickness: 1,
                                  width: defaultPadding / 2,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  title: const Text("Set default address"),
                  trailing: CupertinoSwitch(
                    onChanged: (value) {},
                    value: true,
                    activeColor: primaryColor,
                  ),
                ),
                const SizedBox(height: defaultPadding * 1.5),
                ElevatedButton(
                  onPressed: () {},
                  child: const Text("Save address"),
                )
              ],
            ),
          ),
        ),
      ),
    );
  }
}
