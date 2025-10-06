import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/services/try_on_generation_service.dart';
import 'package:modera/state/cart_item.dart';
import 'package:flutter/foundation.dart';

class TryOnState {
  final String? selectedModel;
  final String? selectedTop;
  final String? selectedBottom;
  final String? generatedImage;
  final bool isGenerating;
  final Map<String, CartItem> cartItems;

  const TryOnState({
    this.selectedModel,
    this.selectedTop,
    this.selectedBottom,
    this.generatedImage,
    this.isGenerating = false,
    this.cartItems = const {},
  });

  TryOnState copyWith({
    String? selectedModel,
    String? selectedTop,
    String? selectedBottom,
    String? generatedImage,
    bool? isGenerating,
    Map<String, CartItem>? cartItems,
  }) {
    return TryOnState(
      selectedModel: selectedModel ?? this.selectedModel,
      selectedTop: selectedTop ?? this.selectedTop,
      selectedBottom: selectedBottom ?? this.selectedBottom,
      generatedImage: generatedImage ?? this.generatedImage,
      isGenerating: isGenerating ?? this.isGenerating,
      cartItems: cartItems ?? this.cartItems,
    );
  }
}

class TryOnNotifier extends Notifier<TryOnState> {
  @override
  TryOnState build() {
    return const TryOnState();
  }
  
  void selectModel(String modelPath) {
    state = state.copyWith(
      selectedModel: modelPath,
      generatedImage: null, // Сбрасываем сгенерированное изображение при смене модели
    );
    TryOnGenerationService.resetLastGeneratedImage();
  }
  
  void selectTop(String topPath) {
    state = state.copyWith(selectedTop: topPath);
    _generateTryOn(TryOnCategory.upperBody, topPath);
  }
  
  void selectBottom(String bottomPath) {
    state = state.copyWith(selectedBottom: bottomPath);
    _generateTryOn(TryOnCategory.lowerBody, bottomPath);
  }
  
  Future<void> _generateTryOn(TryOnCategory category, String garmentPath) async {
    // Проверяем, что модель выбрана
    if (state.selectedModel == null) {
      debugPrint('Модель не выбрана, генерация отменена');
      return;
    }
    
    // Устанавливаем флаг генерации
    state = state.copyWith(isGenerating: true);
    
    try {
      debugPrint('Запуск генерации для категории: ${category.apiValue}, путь к одежде: $garmentPath');
      
      // Запускаем генерацию
      final resultPath = await TryOnGenerationService.generateTryOn(
        userId: '096271a3-6e2e-4cba-96db-e2f20987f27c', // Здесь должен быть ID текущего пользователя
        modelImagePath: state.selectedModel!,
        garmentImagePath: garmentPath,
        category: category,
      );
      
      debugPrint('Генерация завершена, путь к результату: $resultPath');
      
      // Обновляем состояние с путем к сгенерированному изображению
      state = state.copyWith(
        generatedImage: resultPath,
        isGenerating: false,
      );
    } catch (e) {
      debugPrint('Ошибка при генерации: $e');
      // Обрабатываем ошибку
      state = state.copyWith(isGenerating: false);
      // Здесь можно добавить логику обработки ошибок
    }
  }
  
  void addToCart(String imagePath, ItemType type) {
    final existingItem = state.cartItems[imagePath];
    
    if (existingItem != null) {
      // Если товар уже в корзине, увеличиваем количество
      final updatedItem = existingItem.copyWith(
        quantity: existingItem.quantity + 1,
      );
      
      state = state.copyWith(
        cartItems: {
          ...state.cartItems,
          imagePath: updatedItem,
        },
      );
    } else {
      // Если товара нет в корзине, добавляем его
      state = state.copyWith(
        cartItems: {
          ...state.cartItems,
          imagePath: CartItem(
            id: imagePath,
            imagePath: imagePath,
            type: type,
            quantity: 1,
          ),
        },
      );
    }
  }
  
  void updateQuantity(String imagePath, int delta) {
    final existingItem = state.cartItems[imagePath];
    
    if (existingItem != null) {
      final newQuantity = existingItem.quantity + delta;
      
      if (newQuantity <= 0) {
        // Если количество <= 0, удаляем товар из корзины
        final updatedCart = Map<String, CartItem>.from(state.cartItems);
        updatedCart.remove(imagePath);
        
        state = state.copyWith(cartItems: updatedCart);
      } else {
        // Иначе обновляем количество
        state = state.copyWith(
          cartItems: {
            ...state.cartItems,
            imagePath: existingItem.copyWith(quantity: newQuantity),
          },
        );
      }
    }
  }
}

final tryOnProvider = NotifierProvider<TryOnNotifier, TryOnState>(() {
  return TryOnNotifier();
}); 