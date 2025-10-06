import 'package:flutter/material.dart';

import '../../../../constants.dart';
import '../../../../components/list_tile/checkbox_underline_list_tile.dart';

// For Demo
class ColorModel {
  final String title;
  final Color color;
  final int? numOfItems;

  ColorModel({required this.title, this.numOfItems, required this.color});
}
// End for demo

class ProductColorFilter extends StatefulWidget {
  const ProductColorFilter({super.key});

  @override
  State<ProductColorFilter> createState() => _ProductColorFilterState();
}

class _ProductColorFilterState extends State<ProductColorFilter> {
  final List<ColorModel> demoColors = [
    ColorModel(title: "Black", numOfItems: 40, color: Colors.black),
    ColorModel(title: "Blue", numOfItems: 160, color: Colors.blue),
    ColorModel(title: "White", numOfItems: 42, color: Colors.white),
    ColorModel(title: "Purple", numOfItems: 28, color: Colors.purple),
    ColorModel(title: "Pink", numOfItems: 14, color: Colors.pink),
    ColorModel(title: "Red", numOfItems: 14, color: Colors.red),
  ];
  List<ColorModel> filterColors = [];
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
                    "Color",
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
                    demoColors.length,
                    (index) => CheckboxUnderlineListTile(
                      onChanged: (value) {
                        if (value! &&
                            !filterColors.contains(demoColors[index])) {
                          setState(() {
                            filterColors.add(demoColors[index]);
                          });
                        } else if (!value &&
                            filterColors.contains(demoColors[index])) {
                          setState(() {
                            filterColors.remove(demoColors[index]);
                          });
                        }
                      },
                      title: demoColors[index].title,
                      value: filterColors.contains(demoColors[index]),
                      numOfItems: demoColors[index].numOfItems,
                      trailing: Container(
                        height: 20,
                        width: 32,
                        decoration: BoxDecoration(
                          color: demoColors[index].color,
                          borderRadius:
                              const BorderRadius.all(Radius.circular(20)),
                          border:
                              Border.all(color: Theme.of(context).dividerColor),
                        ),
                      ),
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
