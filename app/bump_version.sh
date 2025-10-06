#!/bin/bash

# Function to validate version format
validate_version() {
    if [[ ! $1 =~ ^[0-9]+\.[0-9]+\.[0-9]+\+[0-9]+$ ]]; then
        echo "Invalid version format. Use X.Y.Z+BUILD (e.g., 1.0.1+2)"
        exit 1
    fi
}

# Check if version is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 1.0.1+2"
    exit 1
fi

# Get the new version
NEW_VERSION=$1

# Validate version format
validate_version "$NEW_VERSION"

# Update pubspec.yaml
sed -i '' "s/version: .*$/version: $NEW_VERSION/" pubspec.yaml

# Update iOS version in Info.plist
/usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString ${NEW_VERSION%+*}" ios/Runner/Info.plist
/usr/libexec/PlistBuddy -c "Set :CFBundleVersion ${NEW_VERSION##*+}" ios/Runner/Info.plist

# Update Android version in build.gradle
sed -i '' "s/versionCode [0-9]*/versionCode ${NEW_VERSION##*+}/" android/app/build.gradle
sed -i '' "s/versionName \".*\"/versionName \"${NEW_VERSION%+*}\"/" android/app/build.gradle

# Optional: Regenerate app icons if needed
# flutter pub run flutter_launcher_icons:main

# Clean and get dependencies
flutter clean
flutter pub get

echo "App version updated to $NEW_VERSION"
echo "iOS version: ${NEW_VERSION%+*} (Build ${NEW_VERSION##*+})"
echo "Android version: ${NEW_VERSION%+*} (Code ${NEW_VERSION##*+})" 