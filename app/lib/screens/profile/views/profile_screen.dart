import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:modera/components/list_tile/divider_list_tile.dart';
import 'package:modera/components/network_image_with_loader.dart';
import 'package:modera/constants.dart';
import 'package:modera/route/screen_export.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'components/profile_card.dart';
import 'components/profile_menu_item_list_tile.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Future<void> _logout() async {
    try {
      // Sign out from Supabase
      await SupabaseConfig.supabaseClient.auth.signOut();

      if (!mounted) return;

      // Navigate to signup/login screen
      Navigator.pushNamedAndRemoveUntil(
        context,
        signUpScreenRoute,
        (route) => false,
      );
    } catch (e) {
      if (!mounted) return;

      // Show error if logout fails
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Logout failed: $e'),
          backgroundColor: errorColor,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: ListView(
        children: [
          ProfileCard(
            name: "Evgeniy",
            email: "evgeniy@erarta.ai",
            imageSrc: "https://lh3.googleusercontent.com/fife/ALs6j_E-_eyMVNrwnkSC0l_5YUrEV0zIT91dToif8ZVK6c2Fi2okgshTr3sC8kV9-5lzzeMgWiuqT-KGo4ZfjOrna3T4tTGDvYQsG8JdOduAImuZh98R_dGF7RHhrciqxW98I_xN4RPZHMyb-YW1MQZyOPPQ8xLa5LUxuM9QWDiQkDaexBG4u0L_wSd7P52WpjWob12i1Kppg04UR-8acqEXgxBw5obEA9hO1D8KDV6FZ8IK9P0dalHoQqASFnqRj1dm7-vDMDuXpMjMLUCC2xfdE-9PvLQ_WtssyEm7cyLL1OVXM_wQ4oPNAr1ZK0ibSx7sZV43GZMJyTENXxIweWVPrHnjh8mZFC_xK_lyt7aaAykW6FrdFFc6jPa4P3O2drUiaiIBA9flDWdVw9wDy-JTsiT4s2uh7I2Nvp8wsSbr9x-CAcZiJKpaZm11Gr4MxpsTIYHyqvKDS-FvWhkSmJLx6l6sW057d4YkGSd6gDWuc9zsBA0WgqxasI-wo1iuFUUizZ65R12Y9bmLACw8Zi9ZK5xK6FROzdkw2H8WDbN-wYvwAcvV5WQFH8_yKkiMgrvV5U7GynI43qpBCB41gfndDgjPQko-CZ9ZDXTqN6sfILBugwH35yxx168TgfQolkTI_HbTUc2bDF1rE45Z6fZCASHManL4BUhBjMgJ-q6OBrVsVIcG9rEhatqLbnwcQKDEW0haHiGabcqVwP3t7AOLDZt6oZrqmXDoURa9JXpbh5OHTR44hQG0OPgU_9Gt7w7OTCYg3aZhVZPrIA3wmLEgVo_dfXiExjNQNR8sZzJKUbDqnfs5Io74HIMCGgIV2JXFZxW2Fp-0ESO9t6ojkFELIeI6DlJ4oMtVA-jee3_RSu5PQIUzI83YRgMpFVbV0geh0Z7Gncia_82WmxS1ZEC85ScUVLsN-9_283fDuEdheOJEyr4kfJrrKOJ7som7RKhy8l3S0RoR94fEJBwHn4pd6O9ToWa9rY5mATurJ7qmIv2uu47arb_iZT2-eipD7vEDwqcS_6t8Il1a7HC-ZRy9iW_KWcnYqtRZ46Soh7-PDaKG_YUI1_iy6almGua17M72n6_hemKlgQczEn99qoGwq1ir0Ed9A-vZawb8GK_9en_8yKLIDAzMkUQ8OwaJLPHbFfnghfjdbhab-CKG5dFg9vMuQZySLNcMQB9gEB3uFOFwK9uw6wEAuh-2cOcxFxMTq20Kn8ry_WkZTtd6AhWmRVwG9Wnr44QxMFvTKxcck17Kto-XxaTNH-7sJVf7_d3cjPayEkl1g_wRDj3ILuyk5w1blPS9gBbsjrGHL_gX9jMh3_E2Gq5SUV6bja07J1JwjYHgJ4U6c_719_pGpIYPiCGCNTOzR-_zQT3vNfzDDVwso6HIQUG2Iq1E6_PIiZlGMivr34Bmoi7bMuln2CpPszLG_FCx02BwmzW2I5uRa1DzXKyU0Xa3lYR5YqzthQDbrHQbkyqFEOu5zzGrBQSLrJ_UQV-dd-4OXrVS5Uo4x9gxm9ukkOrpV4iRMeM3B62kqz_l0xECNL6gdLbDx-LuCbiLrRKv2lztNgl7foQlIJoBjG_c40aXUa6W_xZXW_XD-smbUcNH3hyHN1Idsis=w1621-h1186",
            // proLableText: "Sliver",
            // isPro: true, if the user is pro
            press: () {
              Navigator.pushNamed(context, userInfoScreenRoute);
            },
          ),
          Padding(
            padding: const EdgeInsets.symmetric(
                horizontal: defaultPadding, vertical: defaultPadding * 1.5),
            child: GestureDetector(
              onTap: () {},
              child: const AspectRatio(
                aspectRatio: 1.8,
                child:
                    NetworkImageWithLoader("https://i.imgur.com/dz0BBom.png"),
              ),
            ),
          ),

          Padding(
            padding: const EdgeInsets.symmetric(horizontal: defaultPadding),
            child: Text(
              "Account",
              style: Theme.of(context).textTheme.titleSmall,
            ),
          ),
          const SizedBox(height: defaultPadding / 2),
          ProfileMenuListTile(
            text: "Orders",
            svgSrc: "assets/icons/Order.svg",
            press: () {
              Navigator.pushNamed(context, ordersScreenRoute);
            },
          ),
          ProfileMenuListTile(
            text: "Returns",
            svgSrc: "assets/icons/Return.svg",
            press: () {},
          ),
          ProfileMenuListTile(
            text: "Wishlist",
            svgSrc: "assets/icons/Wishlist.svg",
            press: () {},
          ),
          ProfileMenuListTile(
            text: "Addresses",
            svgSrc: "assets/icons/Address.svg",
            press: () {
              Navigator.pushNamed(context, addressesScreenRoute);
            },
          ),
          ProfileMenuListTile(
            text: "Payment",
            svgSrc: "assets/icons/card.svg",
            press: () {
              Navigator.pushNamed(context, emptyPaymentScreenRoute);
            },
          ),
          ProfileMenuListTile(
            text: "Wallet",
            svgSrc: "assets/icons/Wallet.svg",
            press: () {
              Navigator.pushNamed(context, walletScreenRoute);
            },
          ),
          const SizedBox(height: defaultPadding),
          Padding(
            padding: const EdgeInsets.symmetric(
                horizontal: defaultPadding, vertical: defaultPadding / 2),
            child: Text(
              "Personalization",
              style: Theme.of(context).textTheme.titleSmall,
            ),
          ),
          DividerListTileWithTrilingText(
            svgSrc: "assets/icons/Notification.svg",
            title: "Notification",
            trilingText: "Off",
            press: () {
              Navigator.pushNamed(context, enableNotificationScreenRoute);
            },
          ),
          ProfileMenuListTile(
            text: "Preferences",
            svgSrc: "assets/icons/Preferences.svg",
            press: () {
              Navigator.pushNamed(context, preferencesScreenRoute);
            },
          ),
          const SizedBox(height: defaultPadding),
          Padding(
            padding: const EdgeInsets.symmetric(
                horizontal: defaultPadding, vertical: defaultPadding / 2),
            child: Text(
              "Settings",
              style: Theme.of(context).textTheme.titleSmall,
            ),
          ),
          ProfileMenuListTile(
            text: "Language",
            svgSrc: "assets/icons/Language.svg",
            press: () {
              Navigator.pushNamed(context, selectLanguageScreenRoute);
            },
          ),
          ProfileMenuListTile(
            text: "Location",
            svgSrc: "assets/icons/Location.svg",
            press: () {},
          ),
          const SizedBox(height: defaultPadding),
          Padding(
            padding: const EdgeInsets.symmetric(
                horizontal: defaultPadding, vertical: defaultPadding / 2),
            child: Text(
              "Help & Support",
              style: Theme.of(context).textTheme.titleSmall,
            ),
          ),
          ProfileMenuListTile(
            text: "Get Help",
            svgSrc: "assets/icons/Help.svg",
            press: () {
              Navigator.pushNamed(context, getHelpScreenRoute);
            },
          ),
          ProfileMenuListTile(
            text: "FAQ",
            svgSrc: "assets/icons/FAQ.svg",
            press: () {},
            isShowDivider: false,
          ),
          const SizedBox(height: defaultPadding),

          // Log Out
          ListTile(
            onTap: _logout,
            minLeadingWidth: 24,
            leading: SvgPicture.asset(
              "assets/icons/Logout.svg",
              height: 24,
              width: 24,
              colorFilter: const ColorFilter.mode(
                errorColor,
                BlendMode.srcIn,
              ),
            ),
            title: const Text(
              "Log Out",
              style: TextStyle(color: errorColor, fontSize: 14, height: 1),
            ),
          )
        ],
      ),
    );
  }
}
