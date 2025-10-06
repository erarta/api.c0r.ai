import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/screen_export.dart';

import 'components/address_card.dart';

class AddressesScreen extends StatelessWidget {
  const AddressesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Addresses"),
        actions: [
          IconButton(
            onPressed: () {},
            icon: SvgPicture.asset(
              "assets/icons/DotsV.svg",
              colorFilter: ColorFilter.mode(
                  Theme.of(context).iconTheme.color!, BlendMode.srcIn),
            ),
          )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(
            vertical: defaultPadding, horizontal: defaultPadding),
        child: Column(
          children: [
            OutlinedButton.icon(
              onPressed: () {
                Navigator.pushNamed(context, addNewAddressesScreenRoute);
              },
              icon: SvgPicture.asset(
                "assets/icons/Location.svg",
                colorFilter: ColorFilter.mode(
                    Theme.of(context).iconTheme.color!, BlendMode.srcIn),
              ),
              label: Text(
                "Add new address",
                style: TextStyle(
                    color: Theme.of(context).textTheme.bodyLarge!.color),
              ),
            ),
            const SizedBox(height: defaultPadding / 2),
            Padding(
              padding: const EdgeInsets.symmetric(vertical: defaultPadding),
              child: AddressCard(
                title: "My home",
                address:
                    "Sophi Nowakowska, Zabiniec 12/222, 31-215 Cracow, Poland",
                pnNumber: "+79 123 456 789",
                isActive: true,
                press: () {},
              ),
            ),
            AddressCard(
              title: "Office",
              address: "Rio Nowakowska, Zabiniec 12/222, 31-215 Cracow, Poland",
              pnNumber: "+79 123 456 789",
              press: () {},
            ),
          ],
        ),
      ),
    );
  }
}
