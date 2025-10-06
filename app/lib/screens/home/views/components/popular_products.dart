import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/components/product/product_card.dart';
import 'package:modera/route/screen_export.dart';
import '../../../../state/recent_analyses.dart';

import '../../../../constants.dart';

class PopularProducts extends ConsumerWidget {
  const PopularProducts({
    super.key,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncItems = ref.watch(recentAnalysesProvider);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: defaultPadding / 2),
        Padding(
          padding: const EdgeInsets.all(defaultPadding),
          child: Text(
            "Recently analyzed",
            style: Theme.of(context).textTheme.titleSmall,
          ),
        ),
        asyncItems.when(
          loading: () => const SizedBox(height: 220, child: Center(child: CircularProgressIndicator())),
          error: (_, __) => const SizedBox(height: 220),
          data: (items) => SizedBox(
            height: 220,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: items.length,
              itemBuilder: (context, index) {
                final it = items[index];
                return Padding(
                  padding: EdgeInsets.only(
                    left: defaultPadding,
                    right: index == items.length - 1 ? defaultPadding : 0,
                  ),
                  child: ProductCard(
                    image: it.imageUrl,
                    brandName: (it.brand ?? 'Detected').toUpperCase(),
                    title: it.name,
                    price: it.kcalPerServing,
                    priceAfetDiscount: null,
                    dicountpercent: null,
                    press: () {
                      Navigator.pushNamed(context, productDetailsScreenRoute, arguments: true);
                    },
                  ),
                );
              },
            ),
          ),
        ),
      ],
    );
  }
}
