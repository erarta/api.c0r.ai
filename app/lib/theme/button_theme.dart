import 'package:flutter/material.dart';

import '../constants.dart';

// Light theme: dark CTA (black bg, white text)
final ElevatedButtonThemeData elevatedButtonThemeDataLight = ElevatedButtonThemeData(
  style: ButtonStyle(
    padding: MaterialStateProperty.all(const EdgeInsets.all(defaultPadding)),
    minimumSize: MaterialStateProperty.all(const Size(double.infinity, 48)),
    elevation: MaterialStateProperty.all(0),
    shape: MaterialStateProperty.all(
      const RoundedRectangleBorder(
        borderRadius: BorderRadius.all(Radius.circular(defaultBorderRadious)),
      ),
    ),
    backgroundColor: MaterialStateProperty.all(blackColor),
    foregroundColor: MaterialStateProperty.all(Colors.white),
  ),
);

// Dark theme: light CTA (white bg, black text)
final ElevatedButtonThemeData elevatedButtonThemeDataDark = ElevatedButtonThemeData(
  style: ButtonStyle(
    padding: MaterialStateProperty.all(const EdgeInsets.all(defaultPadding)),
    minimumSize: MaterialStateProperty.all(const Size(double.infinity, 48)),
    elevation: MaterialStateProperty.all(0),
    shape: MaterialStateProperty.all(
      const RoundedRectangleBorder(
        borderRadius: BorderRadius.all(Radius.circular(defaultBorderRadious)),
      ),
    ),
    backgroundColor: MaterialStateProperty.all(Colors.white),
    foregroundColor: MaterialStateProperty.all(blackColor),
  ),
);

OutlinedButtonThemeData outlinedButtonTheme(
    {Color borderColor = blackColor10}) {
  return OutlinedButtonThemeData(
    style: OutlinedButton.styleFrom(
      padding: const EdgeInsets.all(defaultPadding),
      minimumSize: const Size(double.infinity, 32),
      side: BorderSide(width: 1.5, color: borderColor),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.all(Radius.circular(defaultBorderRadious)),
      ),
    ),
  );
}

final textButtonThemeData = TextButtonThemeData(
  style: TextButton.styleFrom(foregroundColor: primaryColor),
);
