import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:modera/constants.dart';

class NoAddressScreen extends StatelessWidget {
  const NoAddressScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Address"),
        actions: [
          IconButton(
            onPressed: () {},
            icon: SvgPicture.asset(
              "assets/icons/DotsV.svg",
              colorFilter: ColorFilter.mode(
                  Theme.of(context).iconTheme.color!, BlendMode.srcIn),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          const Spacer(flex: 2),
          Image.asset(
            Theme.of(context).brightness == Brightness.light
                ? "assets/Illustration/EmptyState_lightTheme.png"
                : "assets/Illustration/EmptyState_darkTheme.png",
            width: MediaQuery.of(context).size.width * 0.6,
          ),
          const Spacer(),
          Text(
            "No Address found",
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: defaultPadding),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: defaultPadding * 1.5),
            child: Text(
              "Enabling push notifications allows us to send you info about our new products, sales, events and more!",
              textAlign: TextAlign.center,
            ),
          ),
          const Spacer(flex: 2),
          Padding(
            padding: const EdgeInsets.all(defaultPadding),
            child: ElevatedButton(
              onPressed: () {},
              child: const Text("Add address"),
            ),
          ),
          const Spacer(),
        ],
      ),
    );
  }
}
