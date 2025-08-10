import 'package:flutter/material.dart';

class RulerPicker extends StatefulWidget {
  final double value;
  final double min;
  final double max;
  final double step;
  final double majorTickEvery;
  final String Function(double) labelBuilder;
  final ValueChanged<double> onChanged;
  final ValueChanged<double>? onChangeEnd;

  const RulerPicker({
    super.key,
    required this.value,
    required this.min,
    required this.max,
    this.step = 0.1,
    this.majorTickEvery = 1.0,
    required this.labelBuilder,
    required this.onChanged,
    this.onChangeEnd,
  });

  @override
  State<RulerPicker> createState() => _RulerPickerState();
}

class _RulerPickerState extends State<RulerPicker> {
  late final ScrollController _controller;
  late double _value;
  static const double _pxPerStep = 8; // tune from design

  @override
  void initState() {
    super.initState();
    _value = _clamp(widget.value);
    _controller = ScrollController(initialScrollOffset: _offsetFor(_value));
  }

  @override
  void didUpdateWidget(covariant RulerPicker oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.value != widget.value) {
      _value = _clamp(widget.value);
      _controller.jumpTo(_offsetFor(_value));
    }
  }

  double _clamp(double v) => v.clamp(widget.min, widget.max);

  double _offsetFor(double v) => ((v - widget.min) / widget.step) * _pxPerStep;

  double _valueForOffset(double offset) =>
      (offset / _pxPerStep) * widget.step + widget.min;

  double _snap(double v) {
    final steps = ((v - widget.min) / widget.step).round();
    return _clamp(widget.min + steps * widget.step);
  }

  @override
  Widget build(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(widget.labelBuilder(_value), style: Theme.of(context).textTheme.titleLarge),
        SizedBox(
          height: 80,
          child: NotificationListener<ScrollEndNotification>(
            onNotification: (n) {
              final snapped = _snap(_valueForOffset(_controller.offset));
              _controller.animateTo(_offsetFor(snapped),
                  duration: const Duration(milliseconds: 120), curve: Curves.easeOut);
              _value = snapped;
              widget.onChangeEnd?.call(snapped);
              setState(() {});
              return false;
            },
            child: ListView.builder(
              controller: _controller,
              scrollDirection: Axis.horizontal,
              itemCount: (((widget.max - widget.min) / widget.step).floor()) + 1,
              itemBuilder: (ctx, idx) {
                final val = widget.min + idx * widget.step;
                final isMajor = (val * 100).round() % (widget.majorTickEvery * 100).round() == 0;
                final h = isMajor ? 32.0 : 16.0;
                return SizedBox(
                  width: _pxPerStep,
                  child: Align(
                    alignment: Alignment.bottomCenter,
                    child: Container(
                      width: 2,
                      height: h,
                      color: Theme.of(context)
                          .colorScheme
                          .onSurface
                          .withValues(alpha: 0.6),
                    ),
                  ),
                );
              },
            ),
          ),
        ),
        SizedBox(
          width: width,
          child: CustomPaint(
            painter: _IndicatorPainter(),
            child: const SizedBox(height: 8),
          ),
        )
      ],
    );
  }
}

class _IndicatorPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.redAccent
      ..strokeWidth = 2;
    final x = size.width / 2;
    canvas.drawLine(Offset(x, 0), Offset(x, 8), paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
