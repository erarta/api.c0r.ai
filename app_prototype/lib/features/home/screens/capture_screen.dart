import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/services/api/analyze_api.dart';
import 'package:c0r_app/services/api/models.dart';
import 'package:c0r_app/features/analysis/screens/analysis_result_screen.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';

class CaptureScreen extends StatefulWidget {
  const CaptureScreen({super.key});
  @override
  State<CaptureScreen> createState() => _CaptureScreenState();
}

class _CaptureScreenState extends State<CaptureScreen> {
  File? _image;
  AnalyzeResponse? _result;
  bool _loading = false;

  Future<void> _pick() async {
    final picker = ImagePicker();
    final x = await picker.pickImage(source: ImageSource.camera, imageQuality: 85);
    if (x != null) setState(() => _image = File(x.path));
  }

  Future<void> _analyze() async {
    if (_image == null) return;
    setState(() => _loading = true);
    try {
      final api = await ApiClient.create();
      final analyzeApi = AnalyzeApi(api);
      final res = await analyzeApi.analyze(_image!);
      setState(() => _result = res);
      if (!mounted) return;
      final n = res.analysis.total;
      Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => AnalysisResultScreen(
          calories: n.calories,
          proteins: n.proteins,
          fats: n.fats,
          carbohydrates: n.carbohydrates,
        ),
      ));
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return AppScaffold(
      appBar: AppBar(title: Text(l10n.t('capture.title'))),
      showLoading: _loading,
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            if (_image != null) Image.file(_image!, height: 200),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: FilledButton(onPressed: _pick, child: Text(l10n.t('capture.take_photo')))),
                const SizedBox(width: 12),
                Expanded(child: FilledButton(onPressed: _analyze, child: Text(l10n.t('capture.analyze')))),
              ],
            ),
            const SizedBox(height: 16),
            if (_result != null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(l10n.t('capture.result'), style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: 8),
                      Text('Ккал: ${_result!.analysis.total.calories.toStringAsFixed(0)}'),
                      Text('Белки: ${_result!.analysis.total.proteins.toStringAsFixed(1)}'),
                      Text('Жиры: ${_result!.analysis.total.fats.toStringAsFixed(1)}'),
                      Text('Углеводы: ${_result!.analysis.total.carbohydrates.toStringAsFixed(1)}'),
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
