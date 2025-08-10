"""
Favorites handlers for Telegram bot
Simple flow:
- Save last analysis to favorites
- List favorites with basic pagination
- Add favorite back to daily totals
- Delete favorite
"""
from aiogram import types
from aiogram.fsm.context import FSMContext
from loguru import logger
from typing import List, Dict, Any
import hashlib
import json

from i18n.i18n import i18n
from common.supabase_client import get_or_create_user
from common.db.favorites import save_favorite_food, list_favorites, get_favorite_by_id, delete_favorite
from common.db.logs import get_latest_photo_analysis_log_id, get_log_by_id
from common.calories_manager import add_calories_from_analysis


def _compute_composition_hash(analysis: Dict[str, Any]) -> str:
    food_items = analysis.get('food_items', [])
    try:
        # Sort items by name and weight for deterministic hash
        normalized = [
            {
                'name': (item.get('name') or '').strip().lower(),
                'weight_grams': float(item.get('weight_grams') or 0),
                'calories': float(item.get('calories') or 0),
            }
            for item in food_items
        ]
        normalized.sort(key=lambda x: (x['name'], x['weight_grams'], x['calories']))
        payload = json.dumps(normalized, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()
    except Exception:
        # Fallback to hashing the whole analysis block
        payload = json.dumps(analysis, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def _infer_name_from_analysis(analysis: Dict[str, Any], language: str) -> str:
    dish = analysis.get('regional_analysis', {}).get('dish_identification')
    if dish:
        return dish
    items = analysis.get('food_items', [])
    if items:
        top = ", ".join([item.get('name', '') for item in items[:3] if item.get('name')])
        return (f"салат с {top}" if language == 'ru' else f"salad with {top}") if top else ("Блюдо" if language == 'ru' else "Dish")
    return "Блюдо" if language == 'ru' else "Dish"


async def save_latest_analysis_to_favorites(callback: types.CallbackQuery, state: FSMContext):
    try:
        user = await get_or_create_user(callback.from_user.id)
        language = user.get('language', 'en')
        user_id = user['id']

        log_id = get_latest_photo_analysis_log_id(user_id)
        if not log_id:
            await callback.message.answer(i18n.get_text('error_general', language))
            return
        log_row = get_log_by_id(user_id, log_id)
        meta = (log_row or {}).get('metadata') or {}
        analysis = meta.get('analysis') or {}
        if not analysis:
            await callback.message.answer(i18n.get_text('error_general', language))
            return

        name = _infer_name_from_analysis(analysis, language)
        composition_hash = _compute_composition_hash(analysis)

        saved = await save_favorite_food(user_id=user_id, name=name, items_json={'analysis': analysis}, composition_hash=composition_hash)

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', language), callback_data='action_main_menu')],
            [types.InlineKeyboardButton(text=i18n.get_text('btn_favorites', language, default='⭐ Favorites'), callback_data='action_favorites')]
        ])
        await callback.message.answer(i18n.get_text('favorite_saved', language, default='Saved to favorites ⭐'), reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error saving favorite: {e}")
        await callback.message.answer(i18n.get_text('error_general', 'en'))


async def show_favorites(callback_or_message, page: int = 0):
    """Show favorites list; supports both CallbackQuery and Message origins."""
    is_callback = isinstance(callback_or_message, types.CallbackQuery)
    message = callback_or_message.message if is_callback else callback_or_message
    # IMPORTANT: With callbacks, the real user is callback.from_user, not message.from_user
    telegram_user_id = callback_or_message.from_user.id if is_callback else message.from_user.id
    user = await get_or_create_user(telegram_user_id)
    language = user.get('language', 'en')
    items = await list_favorites(user['id'], limit=50)
    if not items:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', language), callback_data='action_main_menu')]])
        await message.answer(i18n.get_text('favorites_empty', language, default='No favorites yet. Save from analysis with ⭐'), reply_markup=keyboard)
        return

    per_page = 5
    start = page * per_page
    page_items = items[start:start + per_page]

    # Header with pagination controls
    header = i18n.get_text('favorites_title', language, default='⭐ Your Favorites')
    nav_row: List[types.InlineKeyboardButton] = []
    if start > 0:
        nav_row.append(types.InlineKeyboardButton(text='⬅️', callback_data=f'fav_page:{page-1}'))
    if start + per_page < len(items):
        nav_row.append(types.InlineKeyboardButton(text='➡️', callback_data=f'fav_page:{page+1}'))
    header_kb = types.InlineKeyboardMarkup(inline_keyboard=[nav_row] if nav_row else [[types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', language), callback_data='action_main_menu')]])
    await message.answer(header, reply_markup=header_kb)

    # Send each favorite as a separate short message with its own actions
    for it in page_items:
        name = it.get('name', 'Favorite')
        date_str = str(it.get('created_at', ''))[:10]
        # Nutrition extraction
        analysis = (it.get('items_json') or {}).get('analysis') or {}
        tn = analysis.get('total_nutrition', {}) if isinstance(analysis, dict) else {}
        cal = tn.get('calories')
        prot = tn.get('proteins')
        fats = tn.get('fats')
        carbs = tn.get('carbohydrates')

        # Build a friendly, readable block: date → name → KBZhU vertical
        is_ru = (language == 'ru')
        cal_unit = i18n.get_text('cal', language)
        grams_unit = 'г' if is_ru else 'g'
        header_date = f"📅 {date_str}"
        header_name = f"🍽️ {'Блюдо' if is_ru else 'Dish'}: <b>{name}</b>"
        intro = "Мой краткий обзор КБЖУ:" if is_ru else "My quick nutrition snapshot:"
        lines = [header_date, header_name]
        if cal is not None:
            lines.append(intro)
            lines.extend([
                f"🔥 {cal} {cal_unit}",
                f"🥩 {prot} {grams_unit}",
                f"🧈 {fats} {grams_unit}",
                f"🍞 {carbs} {grams_unit}",
            ])
        title = "\n".join(lines)
        fid = it['id']
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text=i18n.get_text('favorite_add_daily', language, default='➕ Add to daily'), callback_data=f'fav_add:{fid}'),
                types.InlineKeyboardButton(text=i18n.get_text('favorite_delete', language, default='🗑️ Delete'), callback_data=f'fav_del:{fid}')
            ]
        ])
        await message.answer(title, reply_markup=kb, parse_mode='HTML')


async def favorites_callback_router(callback: types.CallbackQuery, state: FSMContext):
    try:
        # Acknowledge to stop Telegram spinner
        try:
            await callback.answer()
        except Exception:
            pass
        data = callback.data or ''
        if data == 'action_favorites':
            await show_favorites(callback)
            return
        if data.startswith('fav_page:'):
            page = int(data.split(':', 1)[1])
            await show_favorites(callback, page=page)
            return
        if data.startswith('fav_add:'):
            fid = data.split(':', 1)[1]
            user = await get_or_create_user(callback.from_user.id)
            language = user.get('language', 'en')
            item = await get_favorite_by_id(user['id'], fid)
            if not item:
                await callback.message.answer(i18n.get_text('error_general', language))
                return
            analysis = (item.get('items_json') or {}).get('analysis') or {}
            if not analysis:
                await callback.message.answer(i18n.get_text('error_general', language))
                return
            ok = add_calories_from_analysis(user['id'], {'analysis': analysis})
            if not ok:
                await callback.message.answer(i18n.get_text('error_general', language))
                return
            kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text=i18n.get_text('btn_daily_plan', language), callback_data='action_daily')],
                [types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', language), callback_data='action_main_menu')]
            ])
            await callback.message.answer(i18n.get_text('favorite_added_to_daily', language, default='Added to your daily total ✅'), reply_markup=kb)
            return
        if data.startswith('fav_del:'):
            fid = data.split(':', 1)[1]
            user = await get_or_create_user(callback.from_user.id)
            language = user.get('language', 'en')
            ok = await delete_favorite(user['id'], fid)
            kb = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text=i18n.get_text('btn_favorites', language, default='⭐ Favorites'), callback_data='action_favorites')],
                [types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', language), callback_data='action_main_menu')]
            ])
            if ok:
                await callback.message.answer(i18n.get_text('favorite_deleted', language, default='Deleted from favorites'), reply_markup=kb)
            else:
                await callback.message.answer(i18n.get_text('error_general', language), reply_markup=kb)
            return
    except Exception as e:
        logger.error(f"Favorites callback error: {e}")
        await callback.message.answer(i18n.get_text('error_general', 'en'))


