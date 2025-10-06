import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:modera/components/shopping_bag.dart';
import 'package:modera/constants.dart';
import 'package:modera/screens/search/views/components/search_form.dart';

class SubDiscoverScreen extends StatelessWidget {
  const SubDiscoverScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const List<String> demoManWomanItems = [
      "All Clothing",
      "New in",
      "Coats & Jackets",
      "Dresses",
      "Hoodies & Sweatshirts",
      "Jeans"
    ];
    return Scaffold(
      appBar: AppBar(
        title: const Text("Man’s & Woman’s"),
        actions: const [
          Padding(
            padding: EdgeInsets.all(defaultPadding),
            child: ShoppingBag(),
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
          child: Column(
            children: [
              const Padding(
                padding: EdgeInsets.symmetric(vertical: defaultPadding),
                child: SearchForm(),
              ),
              Expanded(
                child: ListView.builder(
                  itemCount: demoManWomanItems.length,
                  itemBuilder: (context, index) => Column(
                    children: [
                      ListTile(
                        onLongPress: () {},
                        title: Text(
                          demoManWomanItems[index],
                          style: Theme.of(context)
                              .textTheme
                              .bodyLarge!
                              .copyWith(fontWeight: FontWeight.normal),
                        ),
                        trailing: SvgPicture.asset(
                          "assets/icons/miniRight.svg",
                          colorFilter: ColorFilter.mode(
                            Theme.of(context).iconTheme.color!.withOpacity(0.3),
                            BlendMode.srcIn,
                          ),
                          
                        ),
                      ),
                      const Divider(height: 1),
                    ],
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
