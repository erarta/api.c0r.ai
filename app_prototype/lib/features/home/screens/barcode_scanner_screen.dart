import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/core/i18n/app_localizations.dart';

class BarcodeScannerScreen extends StatefulWidget {
  const BarcodeScannerScreen({super.key});
  @override
  State<BarcodeScannerScreen> createState() => _BarcodeScannerScreenState();
}

class _BarcodeScannerScreenState extends State<BarcodeScannerScreen> {
  String? _code;
  bool _locked = false;

  void _onDetect(BarcodeCapture cap) {
    if (_locked) return;
    final codes = cap.barcodes;
    if (codes.isNotEmpty) {
      final raw = codes.first.rawValue;
      if (raw != null && raw.isNotEmpty) {
        setState(() {
          _code = raw;
          _locked = true;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return AppScaffold(
      appBar: AppBar(title: Text(l10n.t('label.title'))),
      body: Stack(
        children: [
          MobileScanner(onDetect: _onDetect),
          if (_code != null)
            Align(
              alignment: Alignment.bottomCenter,
              child: Container(
                color: Colors.black87,
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Expanded(
                      child: Text(
                        'Код: $_code',
                        style: const TextStyle(color: Colors.white),
                      ),
                    ),
                    TextButton(
                      onPressed: () => setState(() => _locked = false),
                      child: const Text('Сканировать снова'),
                    )
                  ],
                ),
              ),
            )
        ],
      ),
    );
  }
}
