# Pickers (DOB, Weight/Height)

## AppDatePicker (DOB)
- Platform-adaptive: CupertinoDatePicker on iOS, showDatePicker (Material) on Android (or force Cupertino for strict pixel match)
- Props:
  - value: DateTime?
  - minDate: DateTime (e.g., now - 120y)
  - maxDate: DateTime (e.g., now - 12y)
  - onChanged(DateTime)
  - onConfirmed(DateTime)
  - onCancelled()
  - mode: date (expandable later)
- Behavior:
  - Opens as a bottom sheet (Cupertino) or dialog (Material)
  - Haptics on wheel snap (iOS)

## RulerPicker (Weight/Height)
- Custom horizontal picker with tick marks and snap behavior
- Props:
  - value: double
  - min: double
  - max: double
  - step: double (e.g., 0.1 kg)
  - majorTickEvery: double (e.g., 1.0 kg)
  - unit: enum { kg, lb, cm, inch }
  - labelBuilder: String Function(double value, Unit unit)
  - onChanged(double value)
  - onChangeEnd(double value)
- Behavior:
  - Center indicator; scrollable scale behind it
  - Haptic feedback on major ticks
  - High-perf: RepaintBoundary, cached tick painter
- Unit conversion helpers:
  - kg<->lb: 1 kg = 2.20462 lb
  - cm<->inch: 1 inch = 2.54 cm

## Design integration
- Typography and colors from AppTheme
- Large tap targets, scroll physics tuned (Clamping on Android, Bouncing on iOS)
- Provide test IDs and deterministic scroll for widget tests
