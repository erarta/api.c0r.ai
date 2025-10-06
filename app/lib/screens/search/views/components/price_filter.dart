import 'package:flutter/material.dart';

import '../../../../constants.dart';
import '../../../../components/list_tile/checkbox_underline_list_tile.dart';

// For Demo
class PriceModel {
  final String title;
  final int? numOfItems;

  PriceModel({required this.title, this.numOfItems});
}
// End for demo

class PriceFilter extends StatefulWidget {
  const PriceFilter({super.key});

  @override
  State<PriceFilter> createState() => _PriceFilterState();
}

class _PriceFilterState extends State<PriceFilter> {
  final List<PriceModel> demoPrices = [
    PriceModel(title: "Under \$25", numOfItems: 10),
    PriceModel(title: "\$25 - \$50", numOfItems: 27),
    PriceModel(title: "\$50 - \$100", numOfItems: 48),
    PriceModel(title: "\$100 - \$300", numOfItems: 13),
    PriceModel(title: "Over \$300", numOfItems: 41),
  ];
  List<PriceModel> filterPrices = [];
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(defaultPadding),
              child: Row(
                children: [
                  const SizedBox(
                    width: 40,
                    child: BackButton(),
                  ),
                  const SizedBox(width: 32),
                  const Spacer(),
                  Text(
                    "Price",
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                  const Spacer(),
                  TextButton(
                    onPressed: () {},
                    child: const Text("Clear All"),
                  )
                ],
              ),
            ),
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  children: List.generate(
                    demoPrices.length,
                    (index) => CheckboxUnderlineListTile(
                      onChanged: (value) {
                        if (value! &&
                            !filterPrices.contains(demoPrices[index])) {
                          setState(() {
                            filterPrices.add(demoPrices[index]);
                          });
                        } else if (!value &&
                            filterPrices.contains(demoPrices[index])) {
                          setState(() {
                            filterPrices.remove(demoPrices[index]);
                          });
                        }
                      },
                      title: demoPrices[index].title,
                      value: filterPrices.contains(demoPrices[index]),
                      numOfItems: demoPrices[index].numOfItems,
                    ),
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(defaultPadding),
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                },
                child: const Text("Done"),
              ),
            )
          ],
        ),
      ),
    );
  }
}
