import 'package:flutter/material.dart';
import 'package:share_plus/share_plus.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';

class ReferFriendScreen extends StatelessWidget {
  const ReferFriendScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      appBar: AppBar(title: const Text('Пригласить друга')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text('Поделись приложением с другом'),
            const SizedBox(height: 12),
            FilledButton(onPressed: () => Share.share('Попробуй c0r.ai! https://c0r.ai'), child: const Text('Поделиться')),
          ],
        ),
      ),
    );
  }
}
