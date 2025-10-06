import 'package:flutter/material.dart';

class LanguageSelector extends StatelessWidget {
  const LanguageSelector({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Use emoji flag instead of image
          const Text(
            '🇺🇸',
            style: TextStyle(fontSize: 16),
          ),
          const SizedBox(width: 4),
          const Text(
            'EN',
            style: TextStyle(
              color: Colors.black,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}