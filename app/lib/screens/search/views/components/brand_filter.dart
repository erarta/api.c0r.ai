import 'package:flutter/material.dart';

import '../../../../constants.dart';
import '../../../../components/list_tile/checkbox_underline_list_tile.dart';

// For Demo
class BrandModel {
  final String name;
  final int? numOfItems;

  BrandModel({required this.name, this.numOfItems});
}
// End for demo

class BrandFilter extends StatefulWidget {
  const BrandFilter({super.key});

  @override
  State<BrandFilter> createState() => _BrandFilterState();
}

class _BrandFilterState extends State<BrandFilter> {
  final List<BrandModel> demoBrand = [
    BrandModel(name: "Abrand", numOfItems: 4),
    BrandModel(name: "AGOLDE", numOfItems: 10),
    BrandModel(name: "Avec Les Filles", numOfItems: 1),
    BrandModel(name: "BDG", numOfItems: 68),
    BrandModel(name: "Blue Revival", numOfItems: 14),
    BrandModel(name: "Daze Denim", numOfItems: 5),
    BrandModel(name: "Kickers", numOfItems: 2),
    BrandModel(name: "Levi’s", numOfItems: 30),
    BrandModel(name: "Lioness", numOfItems: 2),
  ];
  List<BrandModel> filterBrand = [];
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
                    "Brand",
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
                    demoBrand.length,
                    (index) => CheckboxUnderlineListTile(
                      onChanged: (value) {
                        if (value! && !filterBrand.contains(demoBrand[index])) {
                          setState(() {
                            filterBrand.add(demoBrand[index]);
                          });
                        } else if (!value &&
                            filterBrand.contains(demoBrand[index])) {
                          setState(() {
                            filterBrand.remove(demoBrand[index]);
                          });
                        }
                      },
                      title: demoBrand[index].name,
                      value: filterBrand.contains(demoBrand[index]),
                      numOfItems: demoBrand[index].numOfItems,
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
