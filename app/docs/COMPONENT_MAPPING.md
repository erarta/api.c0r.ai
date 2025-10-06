# 🔄 Component Mapping Guide: E-commerce → Food Tracking

## 📋 **Component Transformation Matrix**

### **Direct Reuse (35 components - 74%)**
Components that can be used without any modifications:

#### **Authentication & Navigation**
- ✅ `lib/route/router.dart` - Route generation system
- ✅ `lib/providers/` - All Riverpod providers
- ✅ `lib/theme/` - Theme system (just color updates)
- ✅ `lib/utils/` - All utility functions
- ✅ `lib/config/` - Configuration files
- ✅ `lib/widgets/` - Base widgets

#### **UI Components**
- ✅ `components/network_image_with_loader.dart` - Image loading
- ✅ `components/skleton/` - All skeleton loaders
- ✅ `components/dot_indicators.dart` - Progress indicators
- ✅ `components/blur_container.dart` - Blur effects
- ✅ `components/outlined_active_button.dart` - Buttons
- ✅ `components/list_tile/` - All list components

#### **Chat System (95% reuse)**
- ✅ `screens/chat/views/chat_screen.dart` - Core chat functionality
- ✅ `screens/chat/views/components/text_message.dart` - Message bubbles
- ✅ `screens/chat/views/components/support_person_info.dart` - User info
- ⚠️ `screens/chat/views/components/product_message.dart` → **Rename to `food_message.dart`**

#### **Authentication Screens**
- ✅ `screens/auth/` - Complete authentication flow
- ✅ `screens/user_info/` - User information screens
- ✅ `screens/profile/` - Profile management

---

### **Minor Modifications (8 components - 17%)**
Components needing small changes:

#### **Navigation & Layout**
```dart
// lib/entry_point.dart
// Change bottom navigation labels and icons only
BottomNavigationBarItem(
  // OLD: icon: "Shop.svg", label: "Shop"
  // NEW: icon: "Home.svg", label: "Home"
)
```

#### **Home Screen Structure**
```dart
// screens/home/views/home_screen.dart
// Keep layout, change data source
class HomeScreen extends StatelessWidget {
  // OLD: Products, sales, offers
  // NEW: Daily nutrition, recent meals, tips
}
```

#### **Card Components**
```dart
// components/product/product_card.dart → food/food_card.dart
class FoodCard extends StatelessWidget {
  // Change: Product → Food item
  // Keep: Image, title, subtitle, action button
  final Food food;        // was: Product product
  final int calories;     // was: int price
  final String portion;   // was: String discount
}
```

#### **Banner Components**
```dart
// components/Banner/L/banner_l_style_1.dart
// Keep design, change content
BannerLStyle1(
  // OLD: "Summer Sale", "50% Off"
  // NEW: "Daily Goal", "1,847/2,000 cal"
)
```

---

### **Major Refactors (10 screens - 36%)**
Screens requiring significant changes but keeping core structure:

#### **Shopping Cart → Meal Planning**
```dart
// screens/bookmark/ → screens/meal_plan/
class MealPlanScreen extends StatelessWidget {
  // Transform shopping cart logic to meal planning
  // Keep: List layout, item management, totals
  // Change: Products → Meals, Price → Calories
}
```

#### **Product Details → Food Analysis**
```dart
// screens/product/ → screens/food_analysis/
class FoodAnalysisScreen extends StatelessWidget {
  // Keep: Image gallery, details layout, action buttons
  // Change: Product specs → Nutrition facts
  // Add: Calorie breakdown, macronutrients
}
```

#### **Order History → Food History**
```dart
// screens/order/ → screens/food_history/
class FoodHistoryScreen extends StatelessWidget {
  // Keep: List, filters, date ranges, status tracking
  // Change: Orders → Food entries, Delivery → Meal times
}
```

---

### **New Components (4 components - 9%)**
Components to create from scratch:

#### **Food Scanning**
```dart
// NEW: screens/food_scan/food_scan_screen.dart
class FoodScanScreen extends StatefulWidget {
  // Camera integration
  // Image analysis results
  // Manual food entry fallback
}
```

#### **Nutrition Dashboard**
```dart
// NEW: components/nutrition/daily_progress.dart
class DailyProgress extends StatelessWidget {
  // Circular progress for calories
  // Macronutrient breakdown
  // Daily goals vs actual
}
```

#### **Food Analysis Results**
```dart
// NEW: components/food/nutrition_facts.dart
class NutritionFacts extends StatelessWidget {
  // Nutrition label style display
  // Calorie breakdown
  // Macro and micronutrients
}
```

#### **Nutrition Onboarding**
```dart
// NEW: screens/nutrition_onboarding/
class NutritionOnboardingScreen extends StatefulWidget {
  // Height, weight, activity level
  // Dietary preferences
  // Health goals
}
```

---

## 🔧 **Detailed Transformation Guide**

### **1. Entry Point Changes**
```dart
// lib/entry_point.dart - BEFORE
final List _pages = const [
  HomeScreen(),      // Product browsing
  ChatScreen(),      // Support chat
  BookmarkScreen(),  // Favorites
  CartScreen(),      // Shopping cart
  ProfileScreen(),   // User profile
];

// lib/entry_point.dart - AFTER
final List _pages = const [
  NutritionHomeScreen(),  // Daily dashboard
  ChatScreen(),           // Food analysis chat (95% same)
  FoodScanScreen(),       // Camera food capture
  MealPlanScreen(),       // Meal planning
  ProfileScreen(),        // Profile (100% same)
];
```

### **2. Product Card → Food Card**
```dart
// BEFORE: components/product/product_card.dart
class ProductCard extends StatelessWidget {
  final Product product;
  final String? brandName;
  final VoidCallback? press;

  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: [
          NetworkImageWithLoader(product.image),
          Text(product.title),
          Text('\$${product.price}'),
          Text('${product.discountPercent}% off'),
        ],
      ),
    );
  }
}

// AFTER: components/food/food_card.dart
class FoodCard extends StatelessWidget {
  final FoodItem food;
  final String? mealType;
  final VoidCallback? press;

  Widget build(BuildContext context) {
    return Card(
      child: Column(
        children: [
          NetworkImageWithLoader(food.image),      // Same component!
          Text(food.name),                         // Same layout!
          Text('${food.calories} cal'),            // Different data
          Text('${food.protein}g protein'),        // Different data
        ],
      ),
    );
  }
}
```

### **3. Chat Integration**
```dart
// screens/chat/views/components/product_message.dart → food_message.dart
// BEFORE
class ProductMessage extends StatelessWidget {
  final List<Product> products;

  Widget build(BuildContext context) {
    return Column(
      children: products.map((product) => ProductCard(
        product: product,
        press: () => Navigator.pushNamed(context, productDetailsRoute),
      )).toList(),
    );
  }
}

// AFTER
class FoodMessage extends StatelessWidget {
  final List<FoodRecommendation> foods;

  Widget build(BuildContext context) {
    return Column(
      children: foods.map((food) => FoodCard(
        food: food,
        press: () => Navigator.pushNamed(context, foodDetailsRoute),
      )).toList(),
    );
  }
}
```

### **4. Home Screen Transformation**
```dart
// screens/home/views/home_screen.dart
// BEFORE - E-commerce focus
CustomScrollView(
  slivers: [
    SliverToBoxAdapter(child: OffersCarouselAndCategories()),
    SliverToBoxAdapter(child: PopularProducts()),
    SliverToBoxAdapter(child: FlashSale()),
    SliverToBoxAdapter(child: BestSellers()),
  ],
)

// AFTER - Nutrition focus
CustomScrollView(
  slivers: [
    SliverToBoxAdapter(child: DailyNutritionProgress()),    // New
    SliverToBoxAdapter(child: RecentMeals()),              // Adapted
    SliverToBoxAdapter(child: NutritionTips()),            // Adapted
    SliverToBoxAdapter(child: RecommendedFoods()),         // Adapted
  ],
)
```

---

## 📊 **Data Model Transformations**

### **Product → Food Item**
```dart
// OLD: lib/models/product.dart
class Product {
  final String id;
  final String title;
  final String image;
  final double price;
  final int discountPercent;
  final String brandName;
  final List<String> images;
}

// NEW: lib/models/food_item.dart
class FoodItem {
  final String id;
  final String name;           // was: title
  final String image;          // same
  final int calories;          // was: price
  final double protein;        // was: discountPercent
  final String category;       // was: brandName
  final List<String> images;   // same
  final Map<String, dynamic> nutrition;  // new
}
```

### **Cart → Meal Plan**
```dart
// OLD: Shopping cart logic
class CartItem {
  final Product product;
  final int quantity;
  final double totalPrice;
}

// NEW: Meal plan logic
class MealEntry {
  final FoodItem food;         // was: Product product
  final double portion;        // was: int quantity
  final int totalCalories;     // was: double totalPrice
  final MealType mealType;     // new
  final DateTime consumedAt;   // new
}
```

---

## 🎨 **Asset Transformations**

### **Icons to Replace**
```
assets/icons/
├── Shop.svg → Home.svg (nutrition dashboard)
├── Bag.svg → Camera.svg (food scanning)
├── Heart.svg → Apple.svg (meal planning)
├── Search.svg → Barcode.svg (food search)
├── Profile.svg → Profile.svg (keep same)
└── Chat.svg → Chat.svg (keep same)
```

### **Images to Update**
```
assets/images/
├── app_icon.png → nutrition_app_icon.png
├── onboarding/ → nutrition_onboarding/
└── logo/ → nutrition_logo/
```

---

## 🔗 **Route Transformations**

### **Route Constants Update**
```dart
// lib/route/route_constants.dart
// BEFORE
const String productDetailsRoute = "/product-details";
const String onSaleScreenRoute = "/on-sale";
const String checkoutScreenRoute = "/checkout";
const String cartScreenRoute = "/cart";

// AFTER
const String foodDetailsRoute = "/food-details";        // was: productDetailsRoute
const String nutritionTipsRoute = "/nutrition-tips";    // was: onSaleScreenRoute
const String mealPlanRoute = "/meal-plan";              // was: checkoutScreenRoute
const String foodHistoryRoute = "/food-history";        // was: cartScreenRoute
// NEW routes
const String foodScanRoute = "/food-scan";
const String nutritionOnboardingRoute = "/nutrition-onboarding";
```

---

This mapping ensures systematic transformation while maximizing code reuse and maintaining familiar user experience patterns.