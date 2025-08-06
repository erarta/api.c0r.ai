# 02 – Solution Overview

## Primary Approach: Deep-link token

• On analysis generation the bot stores the JSON in `shared_analyses` and returns a button linking to
`https://t.me/<BOT_USERNAME>?start=share_<token>`.
• Clicking the link triggers `/start share_<token>` → bot retrieves the analysis and sends formatted text.

## Alternative: Native Mobile Sharing

We can also implement **native sharing** using Telegram's built-in share functionality:

### How it works:
1. Bot sends analysis with a **native share button** that triggers the device's share sheet
2. User gets iOS/Android native popup with all installed apps (WhatsApp, Instagram, etc.)
3. Analysis text is formatted for social sharing with hashtags and branding

### Implementation:
```python
# In photo handler, add native share button
native_share_button = types.InlineKeyboardButton(
    text=i18n.get_text('btn_share_native', user_language),
    switch_inline_query_current_chat=f"share_{token}"
)
```

### Pros:
+ Uses native iOS/Android share sheet
+ Works with any installed social app
+ No need for viewers to have the bot
+ Better discoverability on social platforms

### Cons:
- Requires inline mode to be enabled
- Limited to text sharing (no rich formatting)
- Less control over sharing experience

## Recommendation

**Implement both approaches:**
1. **Deep-link** for Telegram-to-Telegram sharing (primary)
2. **Native sharing** for cross-platform social media (secondary)

This gives users maximum flexibility while maintaining the core Telegram experience. 