import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/screens/try_on/components/appearance.dart';
import 'package:modera/screens/try_on/components/fitting_room.dart';
import 'package:modera/services/try_on_generation_service.dart';
import 'package:modera/state/try_on_state.dart';
import 'package:modera/widgets/s3_image.dart';
import 'package:flutter/foundation.dart';
import 'package:modera/services/s3_service.dart';

class TryOnScreen extends ConsumerWidget {
  const TryOnScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(tryOnProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Виртуальная примерочная'),
      ),
      body: Column(
        children: [
          // Область для отображения сгенерированного изображения
          Expanded(
            flex: 3,
            child: Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              child: _buildGeneratedImage(state),
            ),
          ),
          
          // Табы для переключения между выбором модели и одежды
          DefaultTabController(
            length: 2,
            child: Expanded(
              flex: 4,
              child: Column(
                children: [
                  const TabBar(
                    tabs: [
                      Tab(text: 'Модель'),
                      Tab(text: 'Одежда'),
                    ],
                  ),
                  const Expanded(
                    child: TabBarView(
                      children: [
                        Appearance(),
                        FittingRoom(),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildGeneratedImage(TryOnState state) {
    if (state.isGenerating) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Генерация изображения...'),
          ],
        ),
      );
    }
    
    if (state.generatedImage != null) {
      debugPrint('Отображение сгенерированного изображения: ${state.generatedImage}');
      final imageUrl = S3Service.getFileUrl(state.generatedImage!);
      debugPrint('URL сгенерированного изображения: $imageUrl');
      
      return S3Image(
        path: state.generatedImage!,
        fit: BoxFit.contain,
      );
    }
    
    if (state.selectedModel != null) {
      debugPrint('Отображение выбранной модели: ${state.selectedModel}');
      return S3Image(
        path: state.selectedModel!,
        fit: BoxFit.contain,
      );
    }
    
    return const Center(
      child: Text('Выберите модель и одежду для примерки'),
    );
  }
} 