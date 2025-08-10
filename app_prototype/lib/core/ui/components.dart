import 'package:flutter/material.dart';
import 'package:c0r_app/core/theme/tokens.dart';

class AppScreen extends StatelessWidget {
  final String title;
  final Widget child;
  final bool showBack;
  const AppScreen({super.key, required this.title, required this.child, this.showBack = true});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: showBack ? IconButton(icon: const Icon(Icons.arrow_back_ios_new), onPressed: () => Navigator.of(context).maybePop()) : null,
        centerTitle: true,
        title: Text(title, style: Theme.of(context).textTheme.titleLarge),
      ),
      body: SafeArea(
        child: Padding(padding: const EdgeInsets.all(24), child: child),
      ),
    );
  }
}

class AppTitle extends StatelessWidget {
  final String text;
  const AppTitle(this.text, {super.key});
  @override
  Widget build(BuildContext context) {
    return Text(text, style: Theme.of(context).textTheme.displayLarge);
  }
}

class AppSubtitle extends StatelessWidget {
  final String text;
  const AppSubtitle(this.text, {super.key});
  @override
  Widget build(BuildContext context) {
    return Text(text, style: Theme.of(context).textTheme.titleLarge);
  }
}

class AppPrimaryButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  const AppPrimaryButton({super.key, required this.text, required this.onPressed});
  @override
  Widget build(BuildContext context) {
    return SizedBox(width: double.infinity, child: FilledButton(onPressed: onPressed, child: Text(text)));
  }
}

class AppSecondaryButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  const AppSecondaryButton({super.key, required this.text, required this.onPressed});
  @override
  Widget build(BuildContext context) {
    return SizedBox(width: double.infinity, child: OutlinedButton(onPressed: onPressed, child: Text(text)));
  }
}

class AppRadioTile<T> extends StatelessWidget {
  final String label;
  final T value;
  final T groupValue;
  final ValueChanged<T?> onChanged;
  const AppRadioTile({super.key, required this.label, required this.value, required this.groupValue, required this.onChanged});
  @override
  Widget build(BuildContext context) {
    return RadioListTile<T>(
      title: Text(label),
      value: value,
      groupValue: groupValue,
      onChanged: onChanged,
    );
  }
}

class AppCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry padding;
  const AppCard({super.key, required this.child, this.padding = const EdgeInsets.all(AppSpacing.lg)});

  @override
  Widget build(BuildContext context) {
    return Card(child: Padding(padding: padding, child: child));
  }
}

class AppSectionTitle extends StatelessWidget {
  final String text;
  const AppSectionTitle(this.text, {super.key});
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.sm),
      child: Text(text, style: Theme.of(context).textTheme.titleLarge),
    );
  }
}

class AppLabeledProgress extends StatelessWidget {
  final String label;
  final double value;
  final double? target;
  final Color color;
  const AppLabeledProgress({super.key, required this.label, required this.value, this.target, required this.color});

  @override
  Widget build(BuildContext context) {
    final ratio = target == null || target! <= 0 ? 0.0 : (value / target!).clamp(0.0, 1.0);
    final bg = color.withValues(alpha: 0.15);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: Theme.of(context).textTheme.bodyLarge),
            Text(target != null ? '${value.toStringAsFixed(0)} / ${target!.toStringAsFixed(0)}' : value.toStringAsFixed(0)),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(AppRadius.md),
          child: LinearProgressIndicator(
            value: ratio,
            minHeight: 10,
            backgroundColor: bg,
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ),
      ],
    );
  }
}

class AppActionTile extends StatelessWidget {
  final String label;
  final IconData icon;
  final VoidCallback onTap;
  const AppActionTile({super.key, required this.label, required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return InkWell(
      borderRadius: BorderRadius.circular(AppRadius.lg),
      onTap: onTap,
      child: Container(
        width: 160,
        padding: const EdgeInsets.all(AppSpacing.md),
        decoration: BoxDecoration(
          color: scheme.surface,
          borderRadius: BorderRadius.circular(AppRadius.lg),
          border: Border.all(color: scheme.outlineVariant),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: scheme.primary),
            const SizedBox(width: AppSpacing.sm),
            Flexible(child: Text(label, overflow: TextOverflow.ellipsis)),
          ],
        ),
      ),
    );
  }
}

class AppOptionCard<T> extends StatelessWidget {
  final T value;
  final T groupValue;
  final ValueChanged<T> onSelected;
  final String title;
  final String? subtitle;
  final IconData? icon;
  const AppOptionCard({
    super.key,
    required this.value,
    required this.groupValue,
    required this.onSelected,
    required this.title,
    this.subtitle,
    this.icon,
  });

  bool get _selected => value == groupValue;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return InkWell(
      borderRadius: BorderRadius.circular(AppRadius.lg),
      onTap: () => onSelected(value),
      child: Container(
        padding: const EdgeInsets.all(AppSpacing.lg),
        decoration: BoxDecoration(
          color: _selected ? scheme.primary.withValues(alpha: 0.1) : scheme.surface,
          borderRadius: BorderRadius.circular(AppRadius.lg),
          border: Border.all(color: _selected ? scheme.primary : scheme.outlineVariant),
        ),
        child: Row(
          children: [
            if (icon != null) ...[
              Icon(icon, color: _selected ? scheme.primary : scheme.onSurfaceVariant),
              const SizedBox(width: AppSpacing.md),
            ],
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: Theme.of(context).textTheme.titleMedium),
                  if (subtitle != null) ...[
                    const SizedBox(height: 4),
                    Text(subtitle!, style: Theme.of(context).textTheme.bodyMedium),
                  ],
                ],
              ),
            ),
            Icon(_selected ? Icons.radio_button_checked : Icons.radio_button_off, color: _selected ? scheme.primary : scheme.outline)
          ],
        ),
      ),
    );
  }
}
