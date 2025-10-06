import 'package:flutter_riverpod/flutter_riverpod.dart';

class ProfileBasicInfo {
  final String fullName;
  final String phone;
  final String? avatarUrl;
  const ProfileBasicInfo({this.fullName = '', this.phone = '', this.avatarUrl});

  ProfileBasicInfo copyWith({String? fullName, String? phone, String? avatarUrl}) {
    return ProfileBasicInfo(
      fullName: fullName ?? this.fullName,
      phone: phone ?? this.phone,
      avatarUrl: avatarUrl ?? this.avatarUrl,
    );
  }
}

class ProfileBasicNotifier extends StateNotifier<ProfileBasicInfo> {
  ProfileBasicNotifier() : super(const ProfileBasicInfo());
  void setName(String name) => state = state.copyWith(fullName: name);
  void setPhone(String phone) => state = state.copyWith(phone: phone);
  void setAvatar(String url) => state = state.copyWith(avatarUrl: url);
}

final profileBasicProvider = StateNotifierProvider<ProfileBasicNotifier, ProfileBasicInfo>((ref) {
  return ProfileBasicNotifier();
});


