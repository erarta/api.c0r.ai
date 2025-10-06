import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';

import 'package:modera/components/network_image_with_loader.dart';
import 'package:modera/constants.dart';

import 'components/user_info_form.dart';

class EditUserInfoScreen extends StatelessWidget {
  const EditUserInfoScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Profile"),
        actions: [
          IconButton(
            onPressed: () {},
            icon: SvgPicture.asset(
              "assets/icons/info.svg",
              color: Theme.of(context).iconTheme.color,
            ),
          )
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  children: [
                    Stack(
                      clipBehavior: Clip.none,
                      children: [
                        const CircleAvatar(
                          radius: 60,
                          child: NetworkImageWithLoader(
                            "https://lh3.googleusercontent.com/fife/ALs6j_E-_eyMVNrwnkSC0l_5YUrEV0zIT91dToif8ZVK6c2Fi2okgshTr3sC8kV9-5lzzeMgWiuqT-KGo4ZfjOrna3T4tTGDvYQsG8JdOduAImuZh98R_dGF7RHhrciqxW98I_xN4RPZHMyb-YW1MQZyOPPQ8xLa5LUxuM9QWDiQkDaexBG4u0L_wSd7P52WpjWob12i1Kppg04UR-8acqEXgxBw5obEA9hO1D8KDV6FZ8IK9P0dalHoQqASFnqRj1dm7-vDMDuXpMjMLUCC2xfdE-9PvLQ_WtssyEm7cyLL1OVXM_wQ4oPNAr1ZK0ibSx7sZV43GZMJyTENXxIweWVPrHnjh8mZFC_xK_lyt7aaAykW6FrdFFc6jPa4P3O2drUiaiIBA9flDWdVw9wDy-JTsiT4s2uh7I2Nvp8wsSbr9x-CAcZiJKpaZm11Gr4MxpsTIYHyqvKDS-FvWhkSmJLx6l6sW057d4YkGSd6gDWuc9zsBA0WgqxasI-wo1iuFUUizZ65R12Y9bmLACw8Zi9ZK5xK6FROzdkw2H8WDbN-wYvwAcvV5WQFH8_yKkiMgrvV5U7GynI43qpBCB41gfndDgjPQko-CZ9ZDXTqN6sfILBugwH35yxx168TgfQolkTI_HbTUc2bDF1rE45Z6fZCASHManL4BUhBjMgJ-q6OBrVsVIcG9rEhatqLbnwcQKDEW0haHiGabcqVwP3t7AOLDZt6oZrqmXDoURa9JXpbh5OHTR44hQG0OPgU_9Gt7w7OTCYg3aZhVZPrIA3wmLEgVo_dfXiExjNQNR8sZzJKUbDqnfs5Io74HIMCGgIV2JXFZxW2Fp-0ESO9t6ojkFELIeI6DlJ4oMtVA-jee3_RSu5PQIUzI83YRgMpFVbV0geh0Z7Gncia_82WmxS1ZEC85ScUVLsN-9_283fDuEdheOJEyr4kfJrrKOJ7som7RKhy8l3S0RoR94fEJBwHn4pd6O9ToWa9rY5mATurJ7qmIv2uu47arb_iZT2-eipD7vEDwqcS_6t8Il1a7HC-ZRy9iW_KWcnYqtRZ46Soh7-PDaKG_YUI1_iy6almGua17M72n6_hemKlgQczEn99qoGwq1ir0Ed9A-vZawb8GK_9en_8yKLIDAzMkUQ8OwaJLPHbFfnghfjdbhab-CKG5dFg9vMuQZySLNcMQB9gEB3uFOFwK9uw6wEAuh-2cOcxFxMTq20Kn8ry_WkZTtd6AhWmRVwG9Wnr44QxMFvTKxcck17Kto-XxaTNH-7sJVf7_d3cjPayEkl1g_wRDj3ILuyk5w1blPS9gBbsjrGHL_gX9jMh3_E2Gq5SUV6bja07J1JwjYHgJ4U6c_719_pGpIYPiCGCNTOzR-_zQT3vNfzDDVwso6HIQUG2Iq1E6_PIiZlGMivr34Bmoi7bMuln2CpPszLG_FCx02BwmzW2I5uRa1DzXKyU0Xa3lYR5YqzthQDbrHQbkyqFEOu5zzGrBQSLrJ_UQV-dd-4OXrVS5Uo4x9gxm9ukkOrpV4iRMeM3B62kqz_l0xECNL6gdLbDx-LuCbiLrRKv2lztNgl7foQlIJoBjG_c40aXUa6W_xZXW_XD-smbUcNH3hyHN1Idsis=w1621-h1186",
                            radius: 100,
                          ),
                        ),
                        Positioned(
                          bottom: -14,
                          right: -14,
                          child: SizedBox(
                            height: 56,
                            width: 56,
                            child: ElevatedButton(
                              onPressed: () {},
                              style: ElevatedButton.styleFrom(
                                shape: const CircleBorder(),
                                side: BorderSide(
                                    width: 4,
                                    color: Theme.of(context)
                                        .scaffoldBackgroundColor),
                              ),
                              child: SvgPicture.asset(
                                "assets/icons/Edit-Bold.svg",
                                color: Colors.white,
                              ),
                            ),
                          ),
                        )
                      ],
                    ),
                    const SizedBox(height: defaultPadding / 2),
                    TextButton(
                      onPressed: () {},
                      child: const Text("Edit photo"),
                    ),
                    const SizedBox(height: defaultPadding),
                    const UserInfoForm()
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(
                  horizontal: defaultPadding, vertical: defaultPadding / 2),
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                },
                child: const Text("Done"),
              ),
            )
          ],
        ),
      ),
    );
  }
}
