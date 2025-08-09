# Shared Components (Flutter)

Design-driven, platform-adaptive, and testable. Keep props explicit and avoid hidden state.

## Layout
- AppScaffold({ child, showLoading = false, onRetry })
- AppTabScaffold({ tabs: List<TabItem>, initialIndex = 0 })
- AppAppBar({ title, actions = [], leading })

## Controls
- PrimaryButton({ label, onPressed, icon, isBusy = false })
- SecondaryButton({ label, onPressed, icon })
- TertiaryTextButton({ label, onPressed })
- SegmentedControl<T>({ segments: Map<T,String|Widget>, value, onChanged })
- PillToggle({ label, selected, onTap })

## Cards
- AnalysisResultCard({
  imageUrl,
  title,
  kbzhu: { calories, proteins, fats, carbohydrates },
  onFix,
  onDelete,
  onShare,
})
- HealthScoreCard({ score, submetrics: List<MetricItem> })
- GoalSummaryCard({ caloriesTarget, macrosTarget })
- StreakPopup({ streakDays, onDismiss })

## Data Visuals
- MacroRow({ calories, proteins, fats, carbohydrates, targets })
- TrendChart({ series: List<Point>, range: RangePreset })
- BMICard({ bmi, category, min, max })

## Forms
- LabeledValueRow({ label, value, onTap })
- InlineErrorText({ text })
- HelpHintRow({ text, onTap })
- MultiEntryList({ items, onAdd, onRemove, onEdit })

## Lists
- FoodListItem({ title, amountText, macrosText, onTap, onMore })
- DatabaseSearchListItem({ title, subtitle, trailing, onTap })

## Modals / Sheets
- CorrectionSheet({ initial, onSubmit })
- ConfirmSheet({ title, message, confirmText, onConfirm })
- LanguagePickerSheet({ value, options, onChanged })
- GoalAdjustSheet({ initial, onSubmit })
- WeightUpdateSheet({ initialWeight, onSubmit })

## Misc
- EmptyState({ illustration, title, message, actionLabel, onAction })
- LoadingState({ message, progress })

Notes:
- All components support keys for widget tests.
- Colors/typography/spacing come from a theme extension (AppTheme) to match designs.
