import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:modera/components/outlined_active_button.dart';

import '../../../constants.dart';
import 'components/centimeters_size_table.dart';
import 'components/inches_size_table.dart';

class SizeGuideScreen extends StatefulWidget {
  const SizeGuideScreen({super.key});

  @override
  State<SizeGuideScreen> createState() => _SizeGuideScreenState();
}

class _SizeGuideScreenState extends State<SizeGuideScreen> {
  bool _isShowCentimetersSize = false;

  void updateSizes() {
    setState(() {
      _isShowCentimetersSize = !_isShowCentimetersSize;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(
                horizontal: defaultPadding / 2, vertical: defaultPadding),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const BackButton(),
                Text(
                  "Size guide",
                  style: Theme.of(context).textTheme.titleSmall,
                ),
                IconButton(
                  onPressed: () {},
                  icon: SvgPicture.asset("assets/icons/Share.svg",
                      color: Theme.of(context).textTheme.bodyLarge!.color),
                ),
              ],
            ),
          ),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(defaultPadding),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedActiveButton(
                          press: updateSizes,
                          text: "Centimeters",
                          isActive: _isShowCentimetersSize,
                        ),
                      ),
                      const SizedBox(
                        width: defaultPadding,
                      ),
                      Expanded(
                        child: OutlinedActiveButton(
                          isActive: !_isShowCentimetersSize,
                          press: updateSizes,
                          text: "Inches",
                        ),
                      ),
                    ],
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(
                        vertical: defaultPadding * 1.5),
                    child: AnimatedSize(
                      duration: defaultDuration,
                      child: _isShowCentimetersSize
                          ? const CentimetersSizeTable()
                          : const InchesSizeTable(),
                    ),
                  ),
                  Text(
                    "Measurement Guide",
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: defaultPadding / 2),
                    child: Divider(),
                  ),
                  Text(
                    "Bust",
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                  const SizedBox(height: defaultPadding / 2),
                  const Text(
                    "Measure under your arms at the fullest part of your bust. Be sure to go over your shoulder blades.",
                  ),
                  const SizedBox(height: defaultPadding),
                  Text(
                    "Natural Waist",
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                  const SizedBox(height: defaultPadding / 2),
                  const Text(
                    "Measure around the narrowest part of your waistiline with one forefinger between your body and the measuring taps.",
                  ),
                ],
              ),
            ),
          )
        ],
      ),
    );
  }
}
