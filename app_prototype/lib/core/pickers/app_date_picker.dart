import 'dart:io' show Platform;
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';

class AppDatePicker {
  static Future<DateTime?> show(
    BuildContext context, {
    DateTime? initialDate,
    required DateTime firstDate,
    required DateTime lastDate,
  }) async {
    DateTime init = initialDate ?? lastDate;
    if (init.isBefore(firstDate)) init = firstDate;
    if (init.isAfter(lastDate)) init = lastDate;

    if (Platform.isIOS) {
      return showCupertinoModalPopup<DateTime>(
        context: context,
        builder: (ctx) {
          DateTime temp = init;
          return Container(
            height: 280,
            color: Theme.of(context).colorScheme.surface,
            child: Column(
              children: [
                SizedBox(
                  height: 200,
                  child: CupertinoDatePicker(
                    mode: CupertinoDatePickerMode.date,
                    initialDateTime: init,
                    minimumDate: firstDate,
                    maximumDate: lastDate,
                    onDateTimeChanged: (d) => temp = d,
                  ),
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    CupertinoButton(
                      child: const Text('Cancel'),
                      onPressed: () => Navigator.of(ctx).pop(null),
                    ),
                    CupertinoButton(
                      child: const Text('Done'),
                      onPressed: () => Navigator.of(ctx).pop(temp),
                    ),
                  ],
                )
              ],
            ),
          );
        },
      );
    }

    return showDatePicker(
      context: context,
      initialDate: init,
      firstDate: firstDate,
      lastDate: lastDate,
      helpText: 'Select date',
    );
  }
}
