import 'dart:io';

void main(List<String> args) async {
  final minArgIndex = args.indexOf('--min');
  final min = minArgIndex != -1 && minArgIndex + 1 < args.length
      ? double.parse(args[minArgIndex + 1])
      : 0.85;
  final file = File('coverage/lcov.info');
  if (!file.existsSync()) {
    stderr.writeln('coverage/lcov.info not found');
    exit(1);
  }
  final lines = await file.readAsLines();
  int found = 0, hit = 0;
  for (final line in lines) {
    if (line.startsWith('DA:')) {
      final parts = line.substring(3).split(',');
      if (parts.length == 2) {
        found++;
        if (int.tryParse(parts[1]) != 0) hit++;
      }
    }
  }
  final cov = found == 0 ? 0.0 : hit / found;
  stdout.writeln('Coverage: ${(cov * 100).toStringAsFixed(2)}%');
  if (cov + 1e-9 < min) {
    stderr.writeln('Coverage below threshold ${min * 100}%');
    exit(2);
  }
}
