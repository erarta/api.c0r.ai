import 'package:flutter/material.dart';
import 'package:c0r_app/features/extras/screens/food_database_screen.dart';
import 'package:c0r_app/features/favorites/screens/favorites_list_screen.dart';
import 'package:c0r_app/features/recipes/screens/recipes_list_screen.dart';
import 'package:c0r_app/features/settings/screens/buy_credits_screen.dart';
import 'package:c0r_app/core/ui/components.dart';

class QuickActionsPanel extends StatelessWidget {
  const QuickActionsPanel({super.key});
  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: [
        AppActionTile(label: 'Избранное', icon: Icons.favorite_border, onTap: () => _go(context, const FavoritesListScreen())),
        AppActionTile(label: 'Рецепты', icon: Icons.menu_book_outlined, onTap: () => _go(context, const RecipesListScreen())),
        AppActionTile(label: 'База продуктов', icon: Icons.storage_outlined, onTap: () => _go(context, const FoodDatabaseScreen())),
        AppActionTile(label: 'Кредиты', icon: Icons.credit_card, onTap: () => _go(context, const BuyCreditsScreen())),
      ],
    );
  }

  void _go(BuildContext context, Widget screen) {
    Navigator.of(context).push(MaterialPageRoute(builder: (_) => screen));
  }
}

