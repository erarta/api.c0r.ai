import 'package:flutter/material.dart';

import 'search_suggestion_text.dart';

class SearchSuggestions extends StatelessWidget {
  const SearchSuggestions({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    const List<String> demoSuggestion = [
      "White Shirt",
      "Gary Shirt",
      "Yellow Top &  short"
    ];
    return Column(
      children: List.generate(
        demoSuggestion.length,
        (index) => SearchSuggestionText(
          text: demoSuggestion[index],
          press: () {},
        ),
      ),
    );
  }
}
