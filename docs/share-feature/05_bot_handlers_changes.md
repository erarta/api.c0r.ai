# 05 – Bot Handlers Changes

## 1. `common/db/shared_analyses.py`
• Add async CRUD helpers (see 03).

## 2. `services/api/bot/handlers/photo.py`
1. After `analysis_text` is prepared:
```python
from uuid import uuid4
from common.db.shared_analyses import create_shared_analysis
...
 token = uuid4().hex
 await create_shared_analysis(user['id'], token, result)
 
 # Add both share buttons to the analysis message
 deep_link_button = types.InlineKeyboardButton(
     text=i18n.get_text('btn_share_telegram', user_language),
     url=f"https://t.me/{BOT_USERNAME}?start=share_{token}"
 )
 
 native_share_button = types.InlineKeyboardButton(
     text=i18n.get_text('btn_share_native', user_language),
     switch_inline_query_current_chat=f"share_{token}"
 )
 
 # Create keyboard with both share options and main menu
 keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
     [deep_link_button, native_share_button],  # Share buttons in one row
     keyboard.inline_keyboard[0]  # Main menu button below
 ])
```

## 3. `services/api/bot/handlers/commands.py`
• In `start_command` add guard:
```python
if message.text and message.text.startswith('/start share_'):
    token = message.text.split('share_')[1].strip()
    data = await get_shared_analysis(token)
    if not data or is_expired(data):
        await message.answer(i18n.get_text('share_link_invalid', lang))
        return
    formatted = format_analysis_result(data['analysis_json'], lang)
    await message.answer(formatted, parse_mode='Markdown')
    return
```

## 4. `services/api/bot/handlers/inline.py` (NEW FILE)
• Handle inline queries for native sharing:
```python
async def inline_query_handler(query: types.InlineQuery):
    if query.query.startswith('share_'):
        token = query.query.split('share_')[1].strip()
        data = await get_shared_analysis(token)
        if data:
            # Format for social sharing with hashtags
            social_text = format_for_social_sharing(data['analysis_json'])
            await query.answer([
                types.InlineQueryResultArticle(
                    id=token,
                    title=i18n.get_text('share_title', query.from_user.language_code),
                    input_message_content=types.InputTextMessageContent(
                        message_text=social_text,
                        parse_mode='Markdown'
                    )
                )
            ])
```

## 5. `i18n` keys
• `btn_share_telegram`, `btn_share_native`, `share_link_invalid`, `share_link_expired`, `share_title`. 