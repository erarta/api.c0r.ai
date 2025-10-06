import 'package:flutter/material.dart';
import '../../constants.dart';

class RulerPicker extends StatefulWidget {
  const RulerPicker({
    super.key,
    required this.min,
    required this.max,
    required this.initial,
    required this.onChanged,
    this.majorTick = 10,
    this.minorTick = 1,
    this.unit = 'kg',
  });

  final double min;
  final double max;
  final double initial;
  final int majorTick;
  final int minorTick;
  final String unit;
  final ValueChanged<double> onChanged;

  @override
  State<RulerPicker> createState() => _RulerPickerState();
}

class _RulerPickerState extends State<RulerPicker> {
  late FixedExtentScrollController _controller;

  int get itemCount => ((widget.max - widget.min) / widget.minorTick).round() + 1;

  @override
  void initState() {
    final initialIndex = ((widget.initial - widget.min) / widget.minorTick).round();
    _controller = FixedExtentScrollController(initialItem: initialIndex.clamp(0, itemCount - 1));
    super.initState();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final color = Theme.of(context).brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Column(
      children: [
        SizedBox(
          height: 90,
          child: ListWheelScrollView.useDelegate(
            controller: _controller,
            physics: const FixedExtentScrollPhysics(),
            itemExtent: 16,
            perspective: 0.002,
            onSelectedItemChanged: (i) {
              final value = widget.min + i * widget.minorTick;
              widget.onChanged(value);
            },
            childDelegate: ListWheelChildBuilderDelegate(
              childCount: itemCount,
              builder: (context, index) {
                final value = widget.min + index * widget.minorTick;
                final isMajor = (value % widget.majorTick) == 0;
                return CustomPaint(
                  painter: _TickPainter(isMajor: isMajor, color: color),
                );
              },
            ),
          ),
        ),
        const SizedBox(height: defaultPadding),
      ],
    );
  }
}

class _TickPainter extends CustomPainter {
  _TickPainter({required this.isMajor, required this.color});
  final bool isMajor;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 2;
    final length = isMajor ? 18.0 : 10.0;
    canvas.drawLine(Offset(0, 0), Offset(0, length), paint);
  }

  @override
  bool shouldRepaint(covariant _TickPainter oldDelegate) => false;
}


