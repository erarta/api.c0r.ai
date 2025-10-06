import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/services/s3_service.dart';
import 'package:modera/state/try_on_state.dart';
import 'package:modera/state/cart_item.dart';
import 'package:modera/widgets/s3_image.dart';
import 'package:modera/widgets/s3_image_with_check.dart';

class FittingRoom extends ConsumerStatefulWidget {
  const FittingRoom({super.key});

  @override
  ConsumerState<FittingRoom> createState() => _FittingRoomState();
}

class _FittingRoomState extends ConsumerState<FittingRoom> {
  List<String> availableTops = [];
  List<String> availableBottoms = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadAvailableClothes();
  }

  Future<void> _loadAvailableClothes() async {
    // Пути к одежде в S3
    const topsPath = 'assets/tryon/clothes/tops';
    const bottomsPath = 'assets/tryon/clothes/bottoms';
    
    // Генерируем потенциальные пути к одежде
    final List<String> topPaths = List.generate(10, (index) => '$topsPath/${index + 1}.png');
    final List<String> bottomPaths = List.generate(10, (index) => '$bottomsPath/${index + 1}.png');

    // Фильтруем только доступные изображения
    final availableTops = await S3Service.filterAvailableImages(topPaths);
    final availableBottoms = await S3Service.filterAvailableImages(bottomPaths);

    setState(() {
      this.availableTops = availableTops;
      this.availableBottoms = availableBottoms;
      isLoading = false;
    });
  }

  Widget buildClothingItem(String imagePath, VoidCallback onTap, bool isSelected, ItemType type) {
    final cartItem = ref.watch(tryOnProvider).cartItems[imagePath];
    
    return Container(
      width: 120,
      margin: const EdgeInsets.symmetric(horizontal: 8.0),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        border: isSelected
            ? Border.all(color: const Color(0xFF6E50FD), width: 2)
            : null,
      ),
      child: Stack(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: S3ImageWithCheck(
              path: imagePath,
              fit: BoxFit.cover,
              width: double.infinity,
              height: double.infinity,
            ),
          ),
          // Кнопка выбора изображения
          Positioned.fill(
            child: Material(
              color: Colors.transparent,
              child: InkWell(
                borderRadius: BorderRadius.circular(12),
                onTap: onTap,
              ),
            ),
          ),
          // Показываем кнопку корзины всегда, когда есть товар в корзине или элемент выбран
          if (isSelected || cartItem != null)
            Positioned(
              bottom: 0,
              left: 0,
              right: 0,
              child: Material(
                color: const Color(0xFF6E50FD),
                borderRadius: const BorderRadius.only(
                  bottomLeft: Radius.circular(10),
                  bottomRight: Radius.circular(10),
                ),
                child: cartItem == null
                    ? InkWell(
                        onTap: () {
                          ref.read(tryOnProvider.notifier).addToCart(
                            imagePath,
                            type,
                          );
                        },
                        child: Container(
                          height: 22,
                          child: const Center(
                            child: Text(
                              'Add to cart',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: 12,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ),
                      )
                    : Container(
                        height: 22,
                        decoration: const BoxDecoration(
                          borderRadius: BorderRadius.only(
                            bottomLeft: Radius.circular(10),
                            bottomRight: Radius.circular(10),
                          ),
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.only(
                            bottomLeft: Radius.circular(10),
                            bottomRight: Radius.circular(10),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                            children: [
                              InkWell(
                                onTap: () => ref
                                    .read(tryOnProvider.notifier)
                                    .updateQuantity(imagePath, -1),
                                child: const SizedBox(
                                  width: 32,
                                  height: 22,
                                  child: Icon(
                                    Icons.remove,
                                    color: Colors.white,
                                    size: 16,
                                  ),
                                ),
                              ),
                              Text(
                                '${cartItem.quantity}',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 12,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                              InkWell(
                                onTap: () => ref
                                    .read(tryOnProvider.notifier)
                                    .updateQuantity(imagePath, 1),
                                child: const SizedBox(
                                  width: 32,
                                  height: 22,
                                  child: Icon(
                                    Icons.add,
                                    color: Colors.white,
                                    size: 16,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
              ),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Text("Tops", style: Theme.of(context).textTheme.titleMedium),
          ),
          if (availableTops.isNotEmpty)
            SizedBox(
              height: 140,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 8.0),
                itemCount: availableTops.length,
                itemBuilder: (context, index) {
                  final isSelected = ref.watch(tryOnProvider).selectedTop == availableTops[index];
                  return buildClothingItem(
                    availableTops[index],
                    () => ref.read(tryOnProvider.notifier).selectTop(availableTops[index]),
                    isSelected,
                    ItemType.top,
                  );
                },
              ),
            ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Text("Bottoms", style: Theme.of(context).textTheme.titleMedium),
          ),
          if (availableBottoms.isNotEmpty)
            SizedBox(
              height: 140,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 8.0),
                itemCount: availableBottoms.length,
                itemBuilder: (context, index) {
                  final isSelected = ref.watch(tryOnProvider).selectedBottom == availableBottoms[index];
                  return buildClothingItem(
                    availableBottoms[index],
                    () => ref.read(tryOnProvider.notifier).selectBottom(availableBottoms[index]),
                    isSelected,
                    ItemType.bottom,
                  );
                },
              ),
            ),
        ],
      ),
    );
  }
} 