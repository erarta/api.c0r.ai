class CartItem {
  final String id;
  final String imagePath;
  final ItemType type;
  final int quantity;

  CartItem({
    required this.id,
    required this.imagePath,
    required this.type,
    this.quantity = 1,
  });

  CartItem copyWith({
    String? id,
    String? imagePath,
    ItemType? type,
    int? quantity,
  }) {
    return CartItem(
      id: id ?? this.id,
      imagePath: imagePath ?? this.imagePath,
      type: type ?? this.type,
      quantity: quantity ?? this.quantity,
    );
  }
}

enum ItemType {
  top,
  bottom,
  shoes,
} 