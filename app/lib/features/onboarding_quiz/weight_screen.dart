import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_ruler_picker/flutter_ruler_picker.dart';
import 'package:modera/constants.dart';
import 'quiz_state.dart';

class WeightScreen extends ConsumerStatefulWidget {
  const WeightScreen({super.key});

  @override
  ConsumerState<WeightScreen> createState() => _WeightScreenState();
}

class _WeightScreenState extends ConsumerState<WeightScreen> {
  bool _isKg = true;
  late RulerPickerController _controller;
  double _value = 70;

  @override
  void initState() {
    super.initState();
    _controller = RulerPickerController(value: _value);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  double _toDisplay(double kg) => _isKg ? kg : kg * 2.20462;
  double _toKg(double display) => _isKg ? display : display / 2.20462;

  @override
  Widget build(BuildContext context) {
    final answers = ref.watch(onboardingAnswersProvider);
    _value = answers.weightKg ?? _value;
    final display = _toDisplay(_value);

    return Scaffold(
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            final fullWidth = constraints.maxWidth;
            return Stack(
              children: [
                // Header at the top
                Positioned(
                  left: defaultPadding,
                  right: defaultPadding,
                  top: defaultPadding * 1.5,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('What’s your weight?', style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: defaultPadding / 2),
                      Text('Use the ruler to select your current weight.'),
                    ],
                  ),
                ),
                // EXACT center value + unit toggle
                Align(
                  alignment: Alignment.center,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '${display.toStringAsFixed(1)} ${_isKg ? 'kg' : 'lb'}',
                        textAlign: TextAlign.center,
                        style: Theme.of(context)
                            .textTheme
                            .displaySmall
                            ?.copyWith(fontSize: 56, fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: defaultPadding),
                      SegmentedButton<bool>(
                        segments: const [
                          ButtonSegment(value: true, label: Text('kg')),
                          ButtonSegment(value: false, label: Text('lb')),
                        ],
                        selected: {_isKg},
                        onSelectionChanged: (s) {
                          HapticFeedback.selectionClick();
                          setState(() => _isKg = s.first);
                        },
                      ),
                    ],
                  ),
                ),
                // Ruler above the button
                Positioned(
                  left: defaultPadding,
                  right: defaultPadding,
                  bottom: 120,
                  child: Center(
                    child: RulerPicker(
                      controller: _controller,
                      onBuildRulerScaleText: (index, value) => value.toInt().toString(),
                      ranges: const [RulerRange(begin: 30, end: 200, scale: 1)],
                      onValueChanged: (v) {
                        HapticFeedback.selectionClick();
                        final kg = _toKg(v.toDouble());
                        ref.read(onboardingAnswersProvider.notifier).setWeightKg(kg);
                        setState(() => _value = kg);
                      },
                      width: fullWidth - (defaultPadding * 2),
                      height: 100,
                      scaleLineStyleList: const [
                        ScaleLineStyle(color: Colors.grey, height: 30, width: 2),
                        ScaleLineStyle(color: Colors.grey, height: 20, width: 2),
                        ScaleLineStyle(color: Colors.grey, height: 10, width: 1),
                      ],
                      rulerBackgroundColor: Colors.transparent,
                      rulerMarginTop: 8,
                    ),
                  ),
                ),
                // Next button at bottom
                Positioned(
                  left: defaultPadding,
                  right: defaultPadding,
                  bottom: defaultPadding,
                  child: ElevatedButton(
                    onPressed: () {
                      if (mounted) {
                        Navigator.pushNamed(context, '/quiz/age');
                      }
                    },
                    child: const Text('Next'),
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}


