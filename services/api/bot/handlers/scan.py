import os
import httpx
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger
from i18n.i18n import i18n
from common.supabase_client import get_or_create_user

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL")
API_TIMEOUT = 60.0


class ScanStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_grams = State()


async def start_scan_barcode(callback: types.CallbackQuery, state: FSMContext):
    try:
        user = await get_or_create_user(callback.from_user.id)
        user_language = user.get('language', 'en')
        await callback.message.answer(i18n.get_text('scan_barcode_prompt', user_language, default='📷 Send a photo of the product barcode'))
        await state.set_state(ScanStates.waiting_for_photo)
    except Exception as e:
        logger.error(f"Error starting barcode scan: {e}")
        await callback.message.answer(i18n.get_text('error_generic', 'en'))


async def process_barcode_photo(message: types.Message, state: FSMContext):
    try:
        telegram_user_id = message.from_user.id
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        if not message.photo:
            await message.answer(i18n.get_text('scan_barcode_prompt', user_language, default='📷 Please send a barcode photo'))
            return
        # Show progress message with fun facts immediately for engagement
        waiting_phrase = i18n.get_random_waiting_phrase(user_language)
        facts = [i18n.get_random_fact(user_language) for _ in range(3)]
        progress_text = (
            "🔍 Now analyzing your photo...\n\n"
            f"{waiting_phrase}\n\n"
            "💡 Did you know?\n"
            f"{facts[0]}\n\n"
            f"{facts[1]}\n\n"
            f"{facts[2]}"
        )
        progress_msg = await message.answer(progress_text)

        # Optionally display chat action while processing
        try:
            await message.bot.send_chat_action(message.chat.id, 'typing')
        except Exception:
            pass

        photo = message.photo[-1]
        photo_file = await message.bot.get_file(photo.file_id)
        photo_bytes_io = await message.bot.download_file(photo_file.file_path)
        photo_bytes = photo_bytes_io.read() if hasattr(photo_bytes_io, 'read') else photo_bytes_io.getvalue()

        files = {"photo": ("barcode.jpg", photo_bytes, "image/jpeg")}
        data = {"user_language": user_language}
        from shared.auth import get_auth_headers
        headers = get_auth_headers()
        if 'Content-Type' in headers:
            del headers['Content-Type']
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{ML_SERVICE_URL}/api/v1/label/analyze", files=files, data=data, headers=headers, timeout=API_TIMEOUT)
        if resp.status_code != 200:
            await progress_msg.edit_text(i18n.get_text('analysis_failed', user_language))
            await state.clear()
            return
        result = resp.json()
        # Simple rendering for first release
        if result.get('parsed_nutrition') and result['parsed_nutrition'].get('analysis'):
            analysis = result['parsed_nutrition']['analysis']
            tn = analysis.get('total_nutrition', {})
            # Save per-100g for portion calc if available
            per100 = result['parsed_nutrition'].get('analysis', {}).get('provenance', {}).get('per_100g', {})
            product_name = analysis.get('food_items', [{}])[0].get('name', 'Product')
            await state.update_data(per100=per100, product_name=product_name, user_db_id=user['id'])
            txt = (
                f"✅ {i18n.get_text('analysis_complete', user_language)}\n\n"
                f"{i18n.get_text('total_nutrition', user_language)}\n"
                f"{i18n.get_text('calories_label', user_language)}: {tn.get('calories', '?')} {i18n.get_text('cal', user_language)}\n"
                f"{i18n.get_text('proteins_label', user_language)}: {tn.get('proteins', '?')} g\n"
                f"{i18n.get_text('fats_label', user_language)}: {tn.get('fats', '?')} g\n"
                f"{i18n.get_text('carbohydrates_label', user_language)}: {tn.get('carbohydrates', '?')} g\n"
            )
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text=i18n.get_text('ate_this_btn', user_language), callback_data='action_ate_this')],
                [types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', user_language), callback_data='action_main_menu')]
            ])
            await progress_msg.edit_text(txt, parse_mode='Markdown', reply_markup=keyboard)
            return
        else:
            txt = i18n.get_text('scan_no_product_found', user_language, default='No product found. OCR fallback coming in next update.')
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', user_language), callback_data='action_main_menu')]])
            await progress_msg.edit_text(txt, parse_mode='Markdown', reply_markup=keyboard)
            await state.clear()
    except Exception as e:
        logger.error(f"Error processing barcode photo: {e}")
        await message.answer(i18n.get_text('error_generic', 'en'))
        await state.clear()


async def start_enter_grams(callback: types.CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        user_language = 'en'
        # We don't strictly need language here; fetch from DB for better UX
        user = await get_or_create_user(callback.from_user.id)
        if user:
            user_language = user.get('language', 'en')
        if not data.get('per100'):
            await callback.message.answer(i18n.get_text('error_general', user_language))
            await state.clear()
            return
        await callback.message.answer(i18n.get_text('enter_grams_prompt', user_language, default='Enter grams you ate (e.g., 30)'))
        await state.set_state(ScanStates.waiting_for_grams)
    except Exception as e:
        logger.error(f"Error in start_enter_grams: {e}")
        await callback.message.answer(i18n.get_text('error_general', 'en'))


async def process_portion_grams(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        per100 = data.get('per100') or {}
        product_name = data.get('product_name', 'Product')
        user_db_id = data.get('user_db_id')
        user = await get_or_create_user(message.from_user.id)
        user_language = user.get('language', 'en') if user else 'en'
        if not per100 or not user_db_id:
            await message.answer(i18n.get_text('error_general', user_language))
            await state.clear()
            return
        raw = (message.text or '').strip().replace(',', '.')
        try:
            grams = float(raw)
        except Exception:
            await message.answer(i18n.get_text('enter_grams_invalid', user_language, default='Please enter a number, e.g., 30'))
            return
        if grams <= 0 or grams > 2000:
            await message.answer(i18n.get_text('enter_grams_invalid', user_language, default='Please enter a number between 1 and 2000'))
            return

        factor = grams / 100.0
        cals = float(per100.get('calories', 0) or 0) * factor
        prot = float(per100.get('proteins', 0) or 0) * factor
        fats = float(per100.get('fats', 0) or 0) * factor
        carbs = float(per100.get('carbohydrates', 0) or 0) * factor

        # Build analysis payload compatible with calories_manager
        analysis = {
            'analysis': {
                'food_items': [{
                    'name': product_name,
                    'weight_grams': grams,
                    'calories': round(cals, 1),
                    'emoji': '🍽️',
                    'health_benefits': ''
                }],
                'total_nutrition': {
                    'calories': round(cals, 1),
                    'proteins': round(prot, 1),
                    'fats': round(fats, 1),
                    'carbohydrates': round(carbs, 1)
                }
            }
        }

        from common.calories_manager import add_calories_from_analysis
        ok = add_calories_from_analysis(user_db_id, analysis)
        if not ok:
            await message.answer(i18n.get_text('error_general', user_language))
            await state.clear()
            return

        await message.answer(i18n.get_text('portion_added_success', user_language, default='Added to your daily total ✅'))
        await state.clear()
    except Exception as e:
        logger.error(f"Error in process_portion_grams: {e}")
        await message.answer(i18n.get_text('error_general', 'en'))
        await state.clear()


