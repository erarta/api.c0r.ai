import 'package:flutter/material.dart';
import 'package:flutter_svg/svg.dart';
import 'package:modera/constants.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/features/onboarding_quiz/profile_basic_state.dart';
import 'package:modera/services/profile_service.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:modera/route/screen_export.dart';

import 'components/setup_profile_form.dart';
import 'components/user_image_upload.dart';

class ProfileSetupScreen extends ConsumerWidget {
  const ProfileSetupScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        leading: const SizedBox(),
        title: const Text("Setup profile"),
        actions: [
          IconButton(
            onPressed: () {},
            icon: SvgPicture.asset(
              "assets/icons/info.svg",
              colorFilter: ColorFilter.mode(
                Theme.of(context).textTheme.bodyLarge!.color!,
                BlendMode.srcIn,
              ),
            ),
          )
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(defaultPadding),
          child: Column(
            children: [
              Expanded(
                child: SingleChildScrollView(
                  child: Column(
                    children: [
                      UserImageUpload(
                        onUploaded: (url) {
                          ref.read(profileBasicProvider.notifier).setAvatar(url);
                        },
                      ),
                      SizedBox(height: defaultPadding),
                      SetupProfileForm(),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: defaultPadding),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton(
                      onPressed: () {},
                      child: const Text("Skip"),
                    ),
                  ),
                  const SizedBox(width: defaultPadding),
                  Expanded(
                    child: ElevatedButton(
                      onPressed: () async {
                        // Persist basic info temporarily in DB after signup; if already signed in, save now
                        final info = ref.read(profileBasicProvider);
                        final client = Supabase.instance.client;
                        if (client.auth.currentUser != null) {
                          await ProfileService(client).saveContactInfo(
                            fullName: info.fullName,
                            phone: info.phone,
                            avatarUrl: info.avatarUrl,
                          );
                        }
                        if (context.mounted) {
                          Navigator.pushNamed(context, signUpVerificationScreenRoute);
                        }
                      },
                      child: const Text("Sign up"),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
