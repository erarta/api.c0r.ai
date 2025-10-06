import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:modera/components/product/product_card.dart';
import 'package:modera/constants.dart';
import 'package:modera/screens/product/views/product_details_screen.dart'; // Updated import path

class ProductMessage extends StatelessWidget {
  final String message;
  final List<dynamic> products;

  const ProductMessage({
    Key? key,
    required this.message,
    required this.products,
  }) : super(key: key);

  String extractImageUrl(String rawString, int index) {
    try {
      // Clean up the string to make it a valid JSON array
      String jsonString = rawString.replaceAll("'", "\"");

      // Parse the JSON string into a Dart List
      List<String> imageUrls = List<String>.from(json.decode(jsonString));

      // Return the URL at the given index, or an empty string if out of range
      return (index >= 0 && index < imageUrls.length) ? imageUrls[index] : '';
    } catch (e) {
      // Handle any parsing or runtime errors gracefully
      print("Error parsing image URLs: $e");
      return '';
    }
  }

  String extractBaseUrl(String url) {
    // Use split to separate the URL at the `?` character
    return url.split('?')[0];
  }
  

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: defaultPadding),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(message, style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: products.take(5).map<Widget>((product) {
                return Padding(
                  padding: const EdgeInsets.only(right: defaultPadding), // Add padding between cards
                  child: ProductCard(
                    image: extractBaseUrl(extractImageUrl(product['images'], 0)) + ".jpeg",
                    brandName: "Lipsy London",
                    title: product['name'],
                    price: (product['price'] as num).toDouble(),
                    priceAfetDiscount: (product['priceAfetDiscount'] as num?)?.toDouble(),
                    // dicountpercent: (product['dicountpercent'] as num?)?.toDouble(),
                    dicountpercent: 10,
                    press: () {
                      Navigator.push(
                        context, 
                        MaterialPageRoute(
                          builder: (context) => ProductDetailsScreen(
                            isProductAvailable: true,
                            image: extractBaseUrl(extractImageUrl(product['images'], 0)) + ".jpeg",
                          ),
                        ),
                      );
                    },
                  ),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }
} 