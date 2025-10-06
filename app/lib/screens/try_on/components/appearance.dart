import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/services/s3_service.dart';
import 'package:modera/state/try_on_state.dart';
import 'package:modera/widgets/s3_image.dart';
import 'package:modera/widgets/s3_image_with_check.dart';

class Appearance extends ConsumerStatefulWidget {
  const Appearance({super.key});

  @override
  ConsumerState<Appearance> createState() => _AppearanceState();
}

class _AppearanceState extends ConsumerState<Appearance> {
  List<String> availableModels = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadAvailableModels();
  }

  Future<void> _loadAvailableModels() async {
    // Путь к моделям в S3
    const basePath = 'assets/tryon/models-tiles';
    
    // Генерируем потенциальные пути к моделям
    final List<String> modelPaths = List.generate(
      10, 
      (index) => '$basePath/${index + 1}.png'
    );

    // Используем оптимизированный метод для фильтрации доступных изображений
    final availableModels = await S3Service.filterAvailableImages(modelPaths);

    if (mounted) {
      setState(() {
        this.availableModels = availableModels;
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(tryOnProvider);

    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Padding(
      padding: const EdgeInsets.only(
        left: 16.0,
        right: 16.0,
        top: 8.0,
        bottom: 16.0,
      ),
      child: GridView.builder(
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 3,
          childAspectRatio: 0.7,
          crossAxisSpacing: 16,
          mainAxisSpacing: 16,
        ),
        itemCount: availableModels.length,
        itemBuilder: (context, index) {
          final modelImage = availableModels[index];
          final isSelected = state.selectedModel == modelImage;

          return Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(12),
              border: isSelected 
                ? Border.all(color: const Color(0xFF6750A4), width: 2)
                : null,
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: S3ImageWithCheck(
                path: modelImage,
                fit: BoxFit.cover,
                width: double.infinity,
                height: double.infinity,
              ),
            ),
          ).tap(
            onTap: () => ref.read(tryOnProvider.notifier).selectModel(modelImage),
          );
        },
      ),
    );
  }
}

extension TapExtension on Widget {
  Widget tap({required VoidCallback onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: this,
    );
  }
} 