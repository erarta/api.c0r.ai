# 🔍 Debug Instructions for Payment Routing

## Problem
User with English iPhone and English bot language is still being offered YooKassa (99 RUB) instead of Stripe/Stars (USD).

## Debug Steps

### 1. Check Profile Debug Info
```
/buy
```
Look for debug output in terminal showing:
- Telegram `language_code`
- User DB language
- Is CIS region
- Payment provider
- Available providers

### 2. Test Language Change
```
/language
```
Select English, then:
```
/buy
```
Check if payment options change to Stripe/Stars.

### 3. Test Russian Language
```
/language
```
Select Russian, then:
```
/buy
```
Should show YooKassa options.

## Expected Debug Output
For English user, you should see:
```
🔍 PAYMENT DEBUG for user 123456789:
   Telegram language_code: en
   User DB language: en
   Is CIS region: False
   Payment provider: stripe
   Available providers: ['stripe', 'telegram_stars']
   Currency: USD
   Region: international
```

## What to Look For
1. **Telegram language_code**: Should be `en` for English iPhone
2. **User DB language**: Should match Telegram or user's selection
3. **Is CIS region**: Should be `False` for English
4. **Payment provider**: Should be `stripe` for non-CIS
5. **Available providers**: Should include `stripe` and `telegram_stars`

## If Still Showing YooKassa
Check if:
- `language_code` is unexpectedly `ru` or other CIS language
- User DB language is not being updated correctly
- Regional detection logic is working properly

Please run these commands and share the terminal output for analysis.
