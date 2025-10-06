import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/widgets/language_selector.dart';

class MultiSelectListPage extends ConsumerStatefulWidget {
  const MultiSelectListPage({
    super.key,
    required this.title,
    required this.subtitle,
    required this.items,
    required this.initialSelected,
    required this.onChanged,
    required this.onNext,
    this.progressValue = 0.3,
  });

  final String title;
  final String subtitle;
  final List<String> items;
  final Set<String> initialSelected;
  final ValueChanged<Set<String>> onChanged;
  final VoidCallback onNext;
  final double progressValue;

  @override
  ConsumerState<MultiSelectListPage> createState() => _MultiSelectListPageState();
}

class _MultiSelectListPageState extends ConsumerState<MultiSelectListPage> {
  late Set<String> _selected;
  String _query = '';

  @override
  void initState() {
    _selected = {...widget.initialSelected};
    // Auto-select first option for quick testing if nothing selected
    if (_selected.isEmpty && widget.items.isNotEmpty) {
      _selected.add(widget.items.first);
      // Notify parent of the initial selection
      WidgetsBinding.instance.addPostFrameCallback((_) {
        widget.onChanged(_selected);
      });
    }
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    final filtered = widget.items.where((e) => e.toLowerCase().contains(_query.toLowerCase())).toList();
    final showSearch = widget.items.length > 8;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.arrow_back, color: Colors.black),
          ),
          onPressed: () => Navigator.pop(context),
        ),
        title: LinearProgressIndicator(
          value: widget.progressValue,
          backgroundColor: Colors.grey.shade200,
          valueColor: const AlwaysStoppedAnimation<Color>(Colors.black),
        ),
        centerTitle: false,
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 40),
              Text(
                widget.title,
                style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: Colors.black,
                  height: 1.2,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                widget.subtitle,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Colors.grey.shade600,
                ),
              ),
              const SizedBox(height: 40),
              if (showSearch) ...[
                TextField(
                  decoration: InputDecoration(
                    hintText: 'Search',
                    filled: true,
                    fillColor: Colors.grey.shade100,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                  ),
                  onChanged: (v) => setState(() => _query = v),
                ),
                const SizedBox(height: 24),
              ],
              Expanded(
                child: ListView.separated(
                  itemCount: filtered.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 16),
                  itemBuilder: (context, index) {
                    final label = filtered[index];
                    final isSelected = _selected.contains(label);
                    return _QuizOption(
                      label: label,
                      isSelected: isSelected,
                      onTap: () {
                        setState(() {
                          if (isSelected) {
                            _selected.remove(label);
                          } else {
                            _selected.add(label);
                          }
                        });
                        widget.onChanged(_selected);
                      },
                    );
                  },
                ),
              ),
              const SizedBox(height: 24),
              SizedBox(
                height: 56,
                child: ElevatedButton(
                  onPressed: _selected.isNotEmpty ? widget.onNext : null,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _selected.isNotEmpty
                        ? Colors.black
                        : Colors.grey.shade300,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(30),
                    ),
                    disabledBackgroundColor: Colors.grey.shade300,
                    disabledForegroundColor: Colors.grey.shade500,
                  ),
                  child: const Text(
                    'Next',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _QuizOption extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _QuizOption({
    required this.label,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(vertical: 20),
        decoration: BoxDecoration(
          color: isSelected ? Colors.black : Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: isSelected ? Colors.black : Colors.grey.shade300,
            width: 2,
          ),
        ),
        child: Center(
          child: Text(
            label,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: isSelected ? Colors.white : Colors.black,
            ),
          ),
        ),
      ),
    );
  }
}
