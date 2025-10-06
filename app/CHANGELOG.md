# Changelog

All notable changes to this project will be documented in this file.

## [0.2.1] - 2025-10-06

### Changed
- Removed language selector widget from onboarding quiz screens (gender, activity, multi-select)
- Language selection now only available in Profile settings for cleaner UI

## [0.2.0] - 2025-10-05

### Added
- Passwordless OTP authentication using email
- Email OTP verification screen with 6-digit code input
- Auto-verification when last digit is entered
- Shake animation on OTP verification error
- Auto-clear OTP fields after error
- iOS AutoFill support for OTP codes
- Logout functionality in profile screen
- Friendly error messages with orange info style

### Changed
- Removed password field from signup form
- Switched from email/password auth to email-only OTP flow
- Updated signup screen image alignment to show vegetables only
- Improved signup screen UI/UX
- Changed error messages to be more user-friendly

### Fixed
- Navigation flow after successful OTP verification
- Session management on logout

## [0.1.0] - 2025-10-01

### Added
- Initial release
- Onboarding quiz flow
- Basic authentication screens
- Profile screen
- Food tracking features
