import 'package:flutter/material.dart';

class OnboardingImageWidget extends StatelessWidget {
  final String imagePath;

  const OnboardingImageWidget({
    super.key,
    required this.imagePath,
  });

  @override
  Widget build(BuildContext context) {
    final screenHeight = MediaQuery.of(context).size.height;

    return ClipRect(
      child: OverflowBox(
        maxHeight: screenHeight * 1.5, // Make image larger
        alignment: Alignment.topCenter,
        child: Image.asset(
          imagePath,
          fit: BoxFit.cover,
          alignment: const Alignment(0, -0.8), // Focus on the food part only
          errorBuilder: (context, error, stackTrace) {
            // Fallback gradient if image not found
            return Container(
              height: screenHeight,
              width: double.infinity,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [
                    Colors.grey.shade800,
                    Colors.grey.shade900,
                  ],
                ),
              ),
              child: Center(
                child: Icon(
                  Icons.restaurant,
                  size: 100,
                  color: Colors.white.withOpacity(0.3),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}