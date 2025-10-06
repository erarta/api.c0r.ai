import 'package:flutter/material.dart';
import 'package:flutter_widget_from_html_core/flutter_widget_from_html_core.dart';
import 'package:modera/constants.dart';

class ProductInfoScreen extends StatelessWidget {
  const ProductInfoScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
          child: Column(
            children: [
              const SizedBox(height: defaultPadding),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const SizedBox(
                    width: 40,
                    child: BackButton(),
                  ),
                  Text(
                    "Product details",
                    style: Theme.of(context).textTheme.titleSmall,
                  ),
                  const SizedBox(width: 40),
                ],
              ),
              const Expanded(
                child: SingleChildScrollView(
                  padding: EdgeInsets.symmetric(vertical: defaultPadding),
                  child: Column(
                    children: [
                      HtmlWidget(
                        '''
                          <strong>Story</strong>

                          <p>A cool gray cap in soft corduroy. Watch me.' By buying cotton products from Lindex, you’re supporting more responsibly...</p>
                          <strong>Details</strong>
                          <ul>
                            <li>Materials: 100% cotton, and lining Structured</li>
                            <li>Adjustable cotton strap closure</li>
                            <li>High-quality embroidery stitching</li>
                            <li>Head circumference: 21” - 24” / 54-62 cm</li>
                            <li>Embroidery stitching</li>
                            <li>One size fits most</li>
                          </ul>
                          <strong>Style Notes</strong>
                          <p>Style: Summer Hat</p>
                          <p>Design: Plain</p>
                          <p>Fabric: Jersey</p>
                        ''',
                      ),
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
