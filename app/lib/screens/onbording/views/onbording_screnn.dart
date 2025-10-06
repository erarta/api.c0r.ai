import 'package:flutter/material.dart';
import 'package:modera/constants.dart';
import 'package:modera/widgets/language_selector.dart';
import 'onboarding_image_widget.dart';

class OnBordingScreen extends StatefulWidget {
  const OnBordingScreen({super.key});

  @override
  State<OnBordingScreen> createState() => _OnBordingScreenState();
}

class _OnBordingScreenState extends State<OnBordingScreen> {
  late PageController _pageController;
  int _pageIndex = 0;

  final List<OnboardingData> _onboardData = [
    OnboardingData(
      backgroundImage: "assets/images/onboarding_1.jpeg",
      title: "Calorie tracking made easy",
      subtitle: "Just snap a quick photo of your meal and we'll do the rest",
    ),
    OnboardingData(
      backgroundImage: "assets/images/onboarding_2.jpeg",
      title: "In-depth nutrition analyses",
      subtitle: "We will keep your informed about your food choices and their nutritional content",
    ),
    OnboardingData(
      backgroundImage: "assets/images/onboarding_3.jpeg",
      title: "Transform your body",
      subtitle: "Today is the best time to start working toward your dream body",
    ),
  ];

  @override
  void initState() {
    _pageController = PageController(initialPage: 0);
    super.initState();
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Page View with full screen images
          PageView.builder(
            controller: _pageController,
            itemCount: _onboardData.length,
            onPageChanged: (value) {
              setState(() {
                _pageIndex = value;
              });
            },
            itemBuilder: (context, index) => OnboardingPage(
              data: _onboardData[index],
              pageIndex: index,
            ),
          ),


          // Bottom content card with indicators and button
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              decoration: BoxDecoration(
                color: Theme.of(context).scaffoldBackgroundColor,
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(30),
                ),
              ),
              padding: EdgeInsets.only(
                left: 24,
                right: 24,
                top: 40,
                bottom: MediaQuery.of(context).padding.bottom + 24,
              ),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    _onboardData[_pageIndex].title,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    _onboardData[_pageIndex].subtitle,
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Theme.of(context).textTheme.bodyLarge?.color?.withOpacity(0.7),
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 40),

                  // Page indicators
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(
                      _onboardData.length,
                      (index) => Container(
                        margin: const EdgeInsets.symmetric(horizontal: 4),
                        width: 8,
                        height: 8,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: index == _pageIndex
                              ? Theme.of(context).primaryColor
                              : Theme.of(context).primaryColor.withOpacity(0.3),
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 32),

                  // Next button
                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: ElevatedButton(
                      onPressed: () {
                        if (_pageIndex < _onboardData.length - 1) {
                          _pageController.nextPage(
                            duration: const Duration(milliseconds: 300),
                            curve: Curves.easeInOut,
                          );
                        } else {
                          // Navigate to quiz - start with gender
                          Navigator.pushNamed(context, '/quiz/gender');
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.black,
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(30),
                        ),
                      ),
                      child: const Text(
                        'Next',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class OnboardingData {
  final String backgroundImage;
  final String title;
  final String subtitle;

  OnboardingData({
    required this.backgroundImage,
    required this.title,
    required this.subtitle,
  });
}

class OnboardingPage extends StatelessWidget {
  final OnboardingData data;
  final int pageIndex;

  const OnboardingPage({
    super.key,
    required this.data,
    required this.pageIndex,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      fit: StackFit.expand,
      children: [
        // Background image - using custom widget to crop properly
        OnboardingImageWidget(imagePath: data.backgroundImage),

        // Gradient overlay for better text readability
        Positioned(
          bottom: 0,
          left: 0,
          right: 0,
          height: MediaQuery.of(context).size.height * 0.5,
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.transparent,
                  Colors.black.withOpacity(0.3),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}

