import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:typed_data';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:modera/config/supabase_config.dart';
import 'package:modera/services/profile_service.dart';

class UserImageUpload extends StatefulWidget {
  const UserImageUpload({
    super.key,
    required this.onUploaded,
  });

  final ValueChanged<String> onUploaded;

  @override
  State<UserImageUpload> createState() => _UserImageUploadState();
}

class _UserImageUploadState extends State<UserImageUpload> {
  String? _avatarUrl;
  bool _loading = false;

  Future<void> _pickAndUpload() async {
    final picker = ImagePicker();
    final image = await picker.pickImage(source: ImageSource.gallery, maxWidth: 1200, imageQuality: 88);
    if (image == null) return;
    setState(() => _loading = true);
    try {
      final bytes = await image.readAsBytes();
      final client = Supabase.instance.client;
      final user = client.auth.currentUser;
      if (user == null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please sign in first')));
        }
        return;
      }
      final path = 'profile/avatar/${user.id}/${DateTime.now().millisecondsSinceEpoch}.jpg';
      final url = await ProfileService(client).uploadAvatarBytes(SupabaseConfig.storageBucket, path, bytes);
      setState(() => _avatarUrl = url);
      widget.onUploaded(url);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Upload failed: $e')));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        CircleAvatar(
          backgroundColor: Theme.of(context).inputDecorationTheme.fillColor,
          radius: 60,
          child: SizedBox(
            height: 120,
            width: 120,
            child: Stack(
              alignment: Alignment.center,
              children: [
                if (_avatarUrl == null)
                  SvgPicture.asset(
                    "assets/icons/Profile.svg",
                    height: 40,
                    width: 40,
                    colorFilter: ColorFilter.mode(
                      Theme.of(context)
                          .textTheme
                          .bodyLarge!
                          .color!
                          .withOpacity(0.3),
                      BlendMode.srcIn,
                    ),
                  )
                else
                  ClipOval(
                    child: Image.network(_avatarUrl!, width: 120, height: 120, fit: BoxFit.cover),
                  ),
                Positioned(
                  height: 40,
                  width: 40,
                  right: 0,
                  bottom: 0,
                  child: ElevatedButton(
                    onPressed: _loading ? null : _pickAndUpload,
                    style: ElevatedButton.styleFrom(
                      shape: const CircleBorder(),
                      padding: EdgeInsets.zero,
                    ),
                    child: SvgPicture.asset(
                      "assets/icons/Camera-Bold.svg",
                      colorFilter: ColorFilter.mode(
                        Theme.of(context).scaffoldBackgroundColor,
                        BlendMode.srcIn,
                      ),
                    ),
                  ),
                )
              ],
            ),
          ),
        ),
        TextButton(
          onPressed: _loading ? null : _pickAndUpload,
          child: Text(_loading ? 'Uploading...' : 'Upload Image'),
        )
      ],
    );
  }
}
