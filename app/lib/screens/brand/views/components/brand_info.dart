import 'package:flutter/material.dart';
import 'package:modera/components/network_image_with_loader.dart';

import '../../../../constants.dart';

class BrandInfo extends StatelessWidget {
  const BrandInfo({
    super.key,
    required this.image,
    required this.description,
  });

  final String image;
  final String description;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const SizedBox(height: defaultPadding),
        SizedBox(
          height: 48,
          child: NetworkImageWithLoader(
            image,
            fit: BoxFit.contain,
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(vertical: defaultPadding),
          child: Text(
            description,
            textAlign: TextAlign.center,
          ),
        ),
      ],
    );
  }
}
