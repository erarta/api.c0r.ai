import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/services/api/label_api.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';

class LabelAnalyzeScreen extends StatefulWidget {
  const LabelAnalyzeScreen({super.key});
  @override
  State<LabelAnalyzeScreen> createState() => _LabelAnalyzeScreenState();
}

class _LabelAnalyzeScreenState extends State<LabelAnalyzeScreen> {
  File? _image;
  Map<String, dynamic>? _res;
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
      final label = LabelApi(api);
      final data = await label.analyze(_image!);
      setState(() => _res = data);
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return AppScaffold(
      appBar: AppBar(title: Text(l10n.t('label.title'))),
      showLoading: _loading,
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            if (_image != null) Image.file(_image!, height: 200),
            const SizedBox(height: 12),
            Row(children: [
              Expanded(child: FilledButton(onPressed: _pick, child: Text(l10n.t('capture.take_photo')))),
              const SizedBox(width: 12),
              Expanded(child: FilledButton(onPressed: _analyze, child: Text(l10n.t('capture.analyze')))),
            ]),
            const SizedBox(height: 12),
            if (_res != null) Expanded(child: SingleChildScrollView(child: Text(_res.toString()))),
          ],
        ),
      ),
    );
  }
}

