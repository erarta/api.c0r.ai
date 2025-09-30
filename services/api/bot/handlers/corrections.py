from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger
from i18n.i18n import i18n
from common.supabase_client import get_user_by_telegram_id
from common.calories_manager import calories_manager
from common.db.logs import get_latest_photo_analysis_log_id


class FixCaloriesStates(StatesGroup):
    waiting_for_value = State()


async def start_fix_calories_callback(callback: types.CallbackQuery, state: FSMContext):
    try:
        telegram_user_id = callback.from_user.id
        user = await get_user_by_telegram_id(telegram_user_id)
        if not user:
            await callback.message.answer(i18n.get_text('error_general', 'en'))
            return
        user_language = user.get('language', 'en')
        latest_log_id = get_latest_photo_analysis_log_id(user['id'])
        if not latest_log_id:
            await callback.message.answer(i18n.get_text('error_no_recent_analysis', user_language, default='No recent analysis found.'))
            return
        await state.update_data(pending_fix_log_id=latest_log_id, user_db_id=user['id'], user_language=user_language)
        await callback.message.answer(i18n.get_text('enter_corrected_calories', user_language))
        await state.set_state(FixCaloriesStates.waiting_for_value)
    except Exception as e:
        logger.error(f"Error starting fix calories flow: {e}")
        await callback.message.answer(i18n.get_text('error_general', 'en'))


async def process_fix_calories_input(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        user_language = data.get('user_language', 'en')
        log_id = data.get('pending_fix_log_id')
        user_db_id = data.get('user_db_id')
        if not log_id or not user_db_id:
            await message.answer(i18n.get_text('error_general', user_language))
            await state.clear()
            return

        # Parse number
        raw = (message.text or '').strip().replace(',', '.')
        try:
            value = float(raw)
        except Exception:
            await message.answer(i18n.get_text('fix_calories_invalid', user_language))
            return
        if not (1 <= value <= 5000):
            await message.answer(i18n.get_text('fix_calories_invalid', user_language))
            return

        result = calories_manager.apply_calorie_correction(user_db_id, log_id, value)
        if not result or result is False:
            await message.answer(i18n.get_text('error_general', user_language))
            await state.clear()
            return
        # Try to refresh Redis cache for this image if metadata contains image hash
        try:
            from common.db.logs import get_log_by_id
            from common.cache.redis_client import make_cache_key, cache_set_json
            row = get_log_by_id(user_db_id, log_id)
            meta = (row or {}).get('metadata') or {}
            image_hash = meta.get('image_hash') or meta.get('photo_hash')
            if image_hash:
                # Build a minimal cached payload indicating corrected calories for downstream callers
                cached_payload = meta.get('analysis') or {}
                # Attach meta to indicate cache provenance
                cached_payload_meta = {"cache_hit": True, "source": "cache", "corrected_total_calories": float(value)}
                if isinstance(cached_payload, dict):
                    cached_payload.setdefault('meta', {}).update(cached_payload_meta)
                else:
                    cached_payload = {"analysis": {}, "meta": cached_payload_meta}
                cache_key = make_cache_key("analysis", {"user": user_db_id, "image_hash": image_hash})
                await cache_set_json(cache_key, cached_payload, ttl_seconds=14 * 24 * 3600)
        except Exception as _e:
            logger.debug(f"Failed to refresh analysis cache on correction: {_e}")
        # Build informative confirmation with delta and new daily total
        delta = result.get('delta', 0.0)
        new_total = result.get('new_total', 0.0)
        date = result.get('date')
        delta_sign = '+' if delta >= 0 else '−'
        delta_abs = abs(round(delta, 1))
        confirm = i18n.get_text('fix_calories_success', user_language)
        details = i18n.get_text('fix_calories_details', user_language, delta=f"{delta_sign}{delta_abs}", new_total=round(new_total, 1), date=date)
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', user_language), callback_data='action_main_menu')],
            [types.InlineKeyboardButton(text=i18n.get_text('btn_daily_plan', user_language), callback_data='action_daily')]
        ])
        await message.answer(f"{confirm}\n{details}", reply_markup=keyboard)
        await state.clear()
    except Exception as e:
        logger.error(f"Error processing fix calories input: {e}")
        await message.answer(i18n.get_text('error_general', 'en'))
        await state.clear()


