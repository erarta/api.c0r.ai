import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:modera/constants.dart';
import 'package:modera/screens/try_on/components/fitting_room.dart';
import 'package:modera/screens/try_on/components/appearance.dart';
import 'package:modera/state/try_on_state.dart';
import 'package:modera/widgets/s3_image.dart';
import 'package:modera/services/s3_service.dart';

class TryOnScreen extends ConsumerWidget {
  const TryOnScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final selectedModel = ref.watch(tryOnProvider).selectedModel;

    return DefaultTabController(
      length: 2,
      child: Scaffold(
        backgroundColor: const Color(0xFFF5F5F5),
        appBar: AppBar(
          backgroundColor: const Color(0xFFF5F5F5),
          elevation: 0,
          title: const Text("Virtual Try On"),
          leading: IconButton(
            icon: const Icon(Icons.arrow_back),
            onPressed: () => Navigator.of(context).pop(),
          ),
        ),
        body: Column(
          children: [
            // Top part with model preview
            Container(
              height: 400,
              color: const Color(0xFFF8F8F8),
              child: selectedModel != null
                  ? S3Image(
                      path: selectedModel.replaceAll('models-tiles', 'models'),
                      fit: BoxFit.contain,
                    )
                  : S3Image(
                      path: 'assets/tryon/models/1.png',
                      fit: BoxFit.contain,
                    ),
            ),
            // Custom Tab Bar
            DecoratedBox(
              decoration: const BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(20),
                  topRight: Radius.circular(20),
                ),
              ),
              child: Column(
                children: [
                  const SizedBox(height: 16),
                  Stack(
                    children: [
                      TabBar(
                        dividerColor: Colors.transparent,
                        labelColor: Colors.black,
                        unselectedLabelColor: Colors.grey,
                        indicatorColor: Colors.transparent,
                        padding: EdgeInsets.zero,
                        labelPadding: const EdgeInsets.symmetric(horizontal: 2),
                        labelStyle: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                        unselectedLabelStyle: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.normal,
                        ),
                        tabs: const [
                          Tab(text: "Fitting room"),
                          Tab(text: "Appearance"),
                        ],
                      ),
                    ],
                  ),
                ],
              ),
            ),
            // Tab content
            const Expanded(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: Colors.white,
                ),
                child: TabBarView(
                  children: [
                    FittingRoom(),
                    Appearance(),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
} 