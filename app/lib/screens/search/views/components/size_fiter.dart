import 'package:flutter/material.dart';

import '../../../../constants.dart';
import '../../../../components/list_tile/checkbox_underline_list_tile.dart';

// For Demo
class SizeModel {
  final String title;
  final int? numOfItems;

  SizeModel({required this.title, this.numOfItems});
}
// End for demo

class SizeFilter extends StatefulWidget {
  const SizeFilter({super.key});

  @override
  State<SizeFilter> createState() => _SizeFilterState();
}

class _SizeFilterState extends State<SizeFilter> {
  final List<SizeModel> demoSizes = [
    SizeModel(title: "XS", numOfItems: 4),
    SizeModel(title: "S", numOfItems: 10),
    SizeModel(title: "M", numOfItems: 42),
    SizeModel(title: "L", numOfItems: 28),
    SizeModel(title: "XL", numOfItems: 14),
  ];
  List<SizeModel> filterSizes = [];
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
                    "Size",
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
                    demoSizes.length,
                    (index) => CheckboxUnderlineListTile(
                      onChanged: (value) {
                        if (value! && !filterSizes.contains(demoSizes[index])) {
                          setState(() {
                            filterSizes.add(demoSizes[index]);
                          });
                        } else if (!value &&
                            filterSizes.contains(demoSizes[index])) {
                          setState(() {
                            filterSizes.remove(demoSizes[index]);
                          });
                        }
                      },
                      title: demoSizes[index].title,
                      value: filterSizes.contains(demoSizes[index]),
                      numOfItems: demoSizes[index].numOfItems,
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
