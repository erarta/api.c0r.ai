import 'package:flutter/material.dart';
import 'package:c0r_app/core/widgets/app_scaffold.dart';

class ChangeGoalScreen extends StatefulWidget {
  const ChangeGoalScreen({super.key});
  @override
  State<ChangeGoalScreen> createState() => _ChangeGoalScreenState();
}

class _ChangeGoalScreenState extends State<ChangeGoalScreen> {
  String _goal = 'lose';
  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      appBar: AppBar(title: const Text('Цель')),
      body: Column(
        children: [
          RadioListTile(title: const Text('Похудение'), value: 'lose', groupValue: _goal, onChanged: (v) => setState(() => _goal = v as String)),
          RadioListTile(title: const Text('Поддержание'), value: 'maintain', groupValue: _goal, onChanged: (v) => setState(() => _goal = v as String)),
          RadioListTile(title: const Text('Набор массы'), value: 'gain', groupValue: _goal, onChanged: (v) => setState(() => _goal = v as String)),
          const Spacer(),
          Padding(
            padding: const EdgeInsets.all(16),
            child: SizedBox(width: double.infinity, child: FilledButton(onPressed: () {}, child: const Text('Сохранить'))),
          )
        ],
      ),
    );
  }
}
