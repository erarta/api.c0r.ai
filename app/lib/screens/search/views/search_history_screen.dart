import 'package:flutter/material.dart';
import 'package:modera/constants.dart';

import 'components/search_suggestion_text.dart';

class SearchHistoryScreen extends StatelessWidget {
  const SearchHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    const List<String> demoRecentSearch = [
      "White Shirt",
      "Blue short",
      "Red shirt",
      "Gray Dress",
      "Yellow Top &  short"
    ];
    return Scaffold(
      appBar: AppBar(
        title: const Text("History"),
        actions: [
          TextButton(
            onPressed: () {},
            child: const Text("Clear All"),
          )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(defaultPadding),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Today - Saturday (2022 March 29)",
              style: Theme.of(context).textTheme.titleSmall,
            ),
            ...List.generate(
              demoRecentSearch.length,
              (index) => SearchSuggestionText(
                text: demoRecentSearch[index],
                press: () {},
                onTapClose: () {},
              ),
            ),
            const SizedBox(height: defaultPadding * 1.5),
            Text(
              "Yesterday - Saturday, 2021 March 28",
              style: Theme.of(context).textTheme.titleSmall,
            ),
            ...List.generate(
              demoRecentSearch.length,
              (index) => SearchSuggestionText(
                text: demoRecentSearch[index],
                press: () {},
                onTapClose: () {},
              ),
            ),
          ],
        ),
      ),
    );
  }
}
