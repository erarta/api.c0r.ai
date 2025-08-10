import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';

class BmiScreen extends StatelessWidget {
  const BmiScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      appBar: AppBar(title: const Text('BMI')),
      body: const Center(child: Text('BMI график и диапазоны')),
    );
  }
}
