import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';
import 'package:c0r_app/services/api/api_client.dart';
import 'package:c0r_app/services/api/payments_api.dart';

class BuyCreditsScreen extends StatefulWidget {
  const BuyCreditsScreen({super.key});
  @override
  State<BuyCreditsScreen> createState() => _BuyCreditsScreenState();
}

class _BuyCreditsScreenState extends State<BuyCreditsScreen> {
  bool _loading = false;

  Future<void> _buy() async {
    setState(() => _loading = true);
    try {
      final api = await ApiClient.create();
      final pay = PaymentsApi(api);
      await pay.buyCredits(amount: 199.0, planId: 'basic');
    } finally {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      appBar: AppBar(title: const Text('Кредиты')),
      showLoading: _loading,
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text('Купить кредиты для анализа'),
            const SizedBox(height: 12),
            FilledButton(onPressed: _buy, child: const Text('Купить 20 кредитов — 199 ₽')),
          ],
        ),
      ),
    );
  }
}

