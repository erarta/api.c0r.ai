import 'package:flutter_test/flutter_test.dart';
import 'package:c0r_app/services/api/models.dart';

void main() {
  test('DailySummary parses alternative keys', () {
    final json = {
      'date': '2025-01-01',
      'total_calories': 2000,
      'total_proteins': 120,
      'total_fats': 70,
      'total_carbohydrates': 250,
    };
    final d = DailySummary.fromJson(json);
    expect(d.total.calories, 2000);
    expect(d.total.proteins, 120);
    expect(d.total.fats, 70);
    expect(d.total.carbohydrates, 250);
  });

  test('AnalyzeResponse parses nested analysis', () {
    final json = {
      'analysis': {
        'title': 'Meal',
        'total_nutrition': {
          'calories': 500.0,
          'proteins': 30.0,
          'fats': 20.0,
          'carbohydrates': 40.0,
        }
      },
      'daily_summary': {
        'date': '2025-01-01',
        'calories': 1500,
        'proteins': 80,
        'fats': 50,
        'carbohydrates': 180,
      }
    };

    final a = AnalyzeResponse.fromJson(json);
    expect(a.analysis.total.calories, 500);
    expect(a.dailySummary.total.calories, 1500);
  });
}
