class Nutrition {
  final double calories;
  final double proteins;
  final double fats;
  final double carbohydrates;

  Nutrition({required this.calories, required this.proteins, required this.fats, required this.carbohydrates});

  factory Nutrition.fromJson(Map<String, dynamic> j) => Nutrition(
        calories: (j['calories'] ?? 0).toDouble(),
        proteins: (j['proteins'] ?? 0).toDouble(),
        fats: (j['fats'] ?? 0).toDouble(),
        carbohydrates: (j['carbohydrates'] ?? 0).toDouble(),
      );
}

class AnalysisResult {
  final Nutrition total;
  final String? title;
  final String? imageUrl;

  AnalysisResult({required this.total, this.title, this.imageUrl});

  factory AnalysisResult.fromJson(Map<String, dynamic> j) => AnalysisResult(
        total: Nutrition.fromJson(j['analysis']?['total_nutrition'] ?? j['kbzhu'] ?? {}),
        title: j['analysis']?['title'],
        imageUrl: j['analysis']?['image_url'],
      );
}

class DailySummary {
  final String date;
  final Nutrition total;

  DailySummary({required this.date, required this.total});

  factory DailySummary.fromJson(Map<String, dynamic> j) => DailySummary(
        date: j['date'] ?? '',
        total: Nutrition(
          calories: (j['total_calories'] ?? j['calories'] ?? 0).toDouble(),
          proteins: (j['total_proteins'] ?? j['proteins'] ?? 0).toDouble(),
          fats: (j['total_fats'] ?? j['fats'] ?? 0).toDouble(),
          carbohydrates: (j['total_carbohydrates'] ?? j['carbohydrates'] ?? 0).toDouble(),
        ),
      );
}

class AnalyzeResponse {
  final AnalysisResult analysis;
  final DailySummary dailySummary;

  AnalyzeResponse({required this.analysis, required this.dailySummary});

  factory AnalyzeResponse.fromJson(Map<String, dynamic> j) => AnalyzeResponse(
        analysis: AnalysisResult.fromJson(j),
        dailySummary: DailySummary.fromJson(j['daily_summary'] ?? {}),
      );
}
