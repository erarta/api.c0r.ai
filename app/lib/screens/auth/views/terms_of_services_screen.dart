import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:modera/constants.dart';

class TermsOfServicesScreen extends StatelessWidget {
  const TermsOfServicesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        actions: [
          IconButton(
            onPressed: () {},
            icon: SvgPicture.asset(
              "assets/icons/Share.svg",
              colorFilter: ColorFilter.mode(
                Theme.of(context).textTheme.bodyLarge!.color!,
                BlendMode.srcIn,
              ),
              
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text("Last updated Aprill 2020"),
              const SizedBox(height: defaultPadding / 2),
              Text(
                "Terms of services",
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: defaultPadding / 2),
              Expanded(
                child: Scrollbar(
                  thumbVisibility: true,
                  child: SingleChildScrollView(
                    padding:
                        const EdgeInsets.symmetric(vertical: defaultPadding),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "1. Terms",
                          style: Theme.of(context).textTheme.titleSmall,
                        ),
                        const SizedBox(height: defaultPadding / 2),
                        const Text(
                          "Consequat, rhoncus quam auctor non fermentum velit. Sapien mauris amet enim ac nibh enim amet. Lectus orci, id vel sollicitudin. Consequat, eleifend sit consequat amet. Ut hac vulputate tortor, tellus sed sapien ut convallis fringilla. Augue arcu sit odio proin cras purus, nisl. Tempor nunc phasellus tortor at interdum nisl. Nisl consequat aliquet ipsum arcu. Nisl, ullamcorper morbi non integer non vulputate. ",
                        ),
                        const SizedBox(height: defaultPadding),
                        Text(
                          "2. Use license",
                          style: Theme.of(context).textTheme.titleSmall,
                        ),
                        const SizedBox(height: defaultPadding / 2),
                        const Text(
                          "Consequat, rhoncus quam auctor non fermentum velit. Sapien mauris amet enim ac nibh enim amet. Lectus orci, id vel sollicitudin. Consequat, eleifend sit consequat amet. Ut hac vulputate tortor, tellus sed sapien ut convallis fringilla. Augue arcu sit odio proin cras purus, nisl. Tempor nunc phasellus tortor at interdum nisl. Nisl consequat aliquet ipsum arcu. Nisl, ullamcorper morbi non integer non vulputate. Lorem malesuada tempor imperdiet nulla nulla integer et. Tincidunt sit mauris fringilla nunc nibh erat quis auctor. Urna auctor molestie lectus sagittis fringilla tincidunt. Eget justo, odio sit vulputate velit cursus.",
                        ),
                      ],
                    ),
                  ),
                ),
              )
            ],
          ),
        ),
      ),
    );
  }
}
