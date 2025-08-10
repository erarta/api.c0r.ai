import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:c0r_app/features/home/widgets/macro_row.dart';
import 'package:c0r_app/core/theme/theme.dart';

void main() {
  testWidgets('MacroRow renders target values', (tester) async {
    await tester.pumpWidget(MaterialApp(
      theme: buildLightTheme(),
      home: const Scaffold(
        body: MacroRow(
          calories: 1500,
          proteins: 80,
          fats: 50,
          carbohydrates: 180,
          caloriesTarget: 2000,
          proteinsTarget: 120,
          fatsTarget: 70,
          carbsTarget: 250,
        ),
      ),
    ));

    expect(find.textContaining('1500'), findsOneWidget);
    expect(find.textContaining('80'), findsWidgets);
  });
}
