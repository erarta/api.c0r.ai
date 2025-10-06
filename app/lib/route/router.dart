import 'package:flutter/material.dart';
import 'package:modera/entry_point.dart';
import 'package:modera/features/onboarding_quiz/diet_page.dart';
import 'package:modera/features/onboarding_quiz/tastes_page.dart';
import 'package:modera/features/onboarding_quiz/allergens_page.dart';
import 'package:modera/features/onboarding_quiz/cuisines_page.dart';
import 'package:modera/features/onboarding_quiz/dislikes_page.dart';
import 'package:modera/features/onboarding_quiz/weight_screen.dart';
import 'package:modera/features/onboarding_quiz/age_screen.dart';
import 'package:modera/features/onboarding_quiz/gender_screen.dart';
import 'package:modera/features/onboarding_quiz/activity_screen.dart';
import 'package:modera/screens/checkout/views/thanks_for_order_screen.dart';
import 'package:modera/screens/language/view/select_language_screen.dart';
import 'package:modera/screens/payment/views/add_new_card_screen.dart';
import 'package:modera/screens/auth/views/email_verification_screen.dart';
import 'package:modera/screens/auth/views/email_otp_verification_screen.dart';

import 'screen_export.dart';

// Create a global navigator key
final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

Route<dynamic> generateRoute(RouteSettings settings) {
  switch (settings.name) {
    case onbordingScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const OnBordingScreen(),
      );
    case notificationPermissionScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const NotificationPermissionScreen(),
      );
    case preferredLanuageScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const PreferredLanguageScreen(),
      );
    case logInScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const LoginScreen(),
      );
    case signUpScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const SignUpScreen(),
      );
    case profileSetupScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const ProfileSetupScreen(),
      );
    case passwordRecoveryScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const PasswordRecoveryScreen(),
      );
    case verificationMethodScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const VerificationMethodScreen(),
      );
    case otpScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const OtpScreen(),
      );
    case newPasswordScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const SetNewPasswordScreen(),
      );
    case doneResetPasswordScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const DoneResetPasswordScreen(),
      );
    case termsOfServicesScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const TermsOfServicesScreen(),
      );
    case noInternetScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const NoInternetScreen(),
      );
    case serverErrorScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const ServerErrorScreen(),
      );
    case signUpVerificationScreenRoute:
      return MaterialPageRoute(
        builder: (context) {
          final args = settings.arguments as Map<String, dynamic>?;
          final email = args?['email'] as String? ?? '';
          return EmailVerificationScreen(email: email);
        },
      );
    case 'email_otp_verification':
      return MaterialPageRoute(
        builder: (context) {
          final args = settings.arguments as Map<String, dynamic>?;
          final email = args?['email'] as String? ?? '';
          return EmailOtpVerificationScreen(email: email);
        },
      );
    case setupFingerprintScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const SetupFingerprintScreen(),
      );
    case setupFaceIdScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const SetupFaceIdScreen(),
      );
    case productDetailsScreenRoute:
      return MaterialPageRoute(
        builder: (context) {
          bool isProductAvailable = settings.arguments as bool? ?? true;
          return ProductDetailsScreen(isProductAvailable: isProductAvailable);
        },
      );
    case productReviewsScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const ProductReviewsScreen(),
      );
    case addReviewsScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const AddReviewScreen(),
      );
    case homeScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const HomeScreen(),
      );
    case brandScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const BrandScreen(),
      );
    case discoverWithImageScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const DiscoverWithImageScreen(),
      );
    case subDiscoverScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const SubDiscoverScreen(),
      );
    case discoverScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const DiscoverScreen(),
      );
    case onSaleScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const OnSaleScreen(),
      );
    case kidsScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const KidsScreen(),
      );
    case searchScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const SearchScreen(),
      );
    case searchHistoryScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const SearchHistoryScreen(),
      );
    case bookmarkScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const BookmarkScreen(),
      );
    case entryPointScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const EntryPoint(),
      );
    case profileScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const ProfileScreen(),
      );
    case getHelpScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const GetHelpScreen(),
      );
    case chatScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const ChatScreen(),
      );
    case userInfoScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const UserInfoScreen(),
      );
    case currentPasswordScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const CurrentPasswordScreen(),
      );
    case editUserInfoScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const EditUserInfoScreen(),
      );
    case notificationsScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const NotificationsScreen(),
      );
    case noNotificationScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const NoNotificationScreen(),
      );
    case enableNotificationScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const EnableNotificationScreen(),
      );
    case notificationOptionsScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const NotificationOptionsScreen(),
      );
    case selectLanguageScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const SelectLanguageScreen(),
      );
    case '/quiz/gender':
      return MaterialPageRoute(builder: (context) => const GenderScreen());
    case '/quiz/activity':
      return MaterialPageRoute(builder: (context) => const ActivityScreen());
    case '/quiz/diet':
      return MaterialPageRoute(builder: (context) => const DietPage());
    case '/quiz/tastes':
      return MaterialPageRoute(builder: (context) => const TastesPage());
    case '/quiz/allergens':
      return MaterialPageRoute(builder: (context) => const AllergensPage());
    case '/quiz/cuisines':
      return MaterialPageRoute(builder: (context) => const CuisinesPage());
    case '/quiz/dislikes':
      return MaterialPageRoute(builder: (context) => const DislikesPage());
    case '/quiz/weight':
      return MaterialPageRoute(builder: (context) => const WeightScreen());
    case '/quiz/age':
      return MaterialPageRoute(builder: (context) => const AgeScreen());
    case noAddressScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const NoAddressScreen(),
      );
    case addressesScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const AddressesScreen(),
      );
    case addNewAddressesScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const AddNewAddressScreen(),
      );
    case ordersScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const OrdersScreen(),
      );
    case orderProcessingScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const OrderProcessingScreen(),
      );
    case orderDetailsScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const OrderDetailsScreen(),
      );
    case cancleOrderScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const CancleOrderScreen(),
      );
    case deliveredOrdersScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const DelivereOrdersdScreen(),
      );
    case cancledOrdersScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const CancledOrdersScreen(),
      );
    case preferencesScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const PreferencesScreen(),
      );
    case emptyPaymentScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const EmptyPaymentScreen(),
      );
    case emptyWalletScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const EmptyWalletScreen(),
      );
    case walletScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const WalletScreen(),
      );
    case cartScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const CartScreen(),
      );
    case paymentMethodScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const PaymentMethodScreen(),
      );
    case addNewCardScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const AddNewCardScreen(),
      );
    case thanksForOrderScreenRoute:
      return MaterialPageRoute(
        builder: (context) => const ThanksForOrderScreen(),
      );
    default:
      return MaterialPageRoute(
        // Make a screen for undefine
        builder: (context) => const OnBordingScreen(),
      );
  }
}
