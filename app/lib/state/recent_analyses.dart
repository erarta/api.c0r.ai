import 'package:flutter_riverpod/flutter_riverpod.dart';

class FoodAnalysisItem {
  final String id;
  final String name;
  final String? brand;
  final String imageUrl;
  final double kcalPerServing;

  const FoodAnalysisItem({
    required this.id,
    required this.name,
    required this.imageUrl,
    required this.kcalPerServing,
    this.brand,
  });
}

final selectedDateProvider = StateProvider<DateTime>((ref) {
  final now = DateTime.now();
  return DateTime(now.year, now.month, now.day);
});

final recentAnalysesProvider = FutureProvider.autoDispose<List<FoodAnalysisItem>>((ref) async {
  ref.watch(selectedDateProvider); // triggers reload on date change
  // TODO: integrate real API. Temporary mocked list to keep UI working.
  await Future<void>.delayed(const Duration(milliseconds: 150));
  return List.generate(8, (i) {
    return FoodAnalysisItem(
      id: 'mock-$i',
      name: 'Analyzed Food ${i + 1}',
      brand: 'Detected',
      imageUrl: 'https://i.imgur.com/CGCyp1d.png',
      kcalPerServing: 240 + i * 15,
    );
  });
});


