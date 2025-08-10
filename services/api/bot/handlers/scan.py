import os
import httpx
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger
from i18n.i18n import i18n
from common.supabase_client import get_or_create_user
from common.db.profiles import get_user_profile

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL")
# Perplexity label analysis can take longer; allow sufficient timeout
API_TIMEOUT = 25.0


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
        logger.info("[SCAN] process_barcode_photo entered")
        telegram_user_id = message.from_user.id
        user = await get_or_create_user(telegram_user_id)
        user_language = user.get('language', 'en')
        if not ML_SERVICE_URL:
            logger.error("[SCAN] ML_SERVICE_URL is not set")
            await message.answer(i18n.get_text('analysis_failed', user_language))
            await state.clear()
            return
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

        # Use a medium-sized photo to reduce upload time per Habr best-practices
        photo = message.photo[-2] if len(message.photo) > 1 else message.photo[-1]
        photo_file = await message.bot.get_file(photo.file_id)
        photo_bytes_io = await message.bot.download_file(photo_file.file_path)
        photo_bytes = photo_bytes_io.read() if hasattr(photo_bytes_io, 'read') else photo_bytes_io.getvalue()
        logger.info(f"[SCAN] Downloaded photo bytes={len(photo_bytes)}")

        files = {"photo": ("barcode.jpg", photo_bytes, "image/jpeg")}
        data = {"user_language": user_language}
        from shared.auth import get_auth_headers
        headers = get_auth_headers()
        if 'Content-Type' in headers:
            del headers['Content-Type']
        async with httpx.AsyncClient() as client:
            # Switch to Perplexity-based label analysis for richer results
            url = f"{ML_SERVICE_URL}/api/v1/label/perplexity"
            logger.info(f"[SCAN] POST {url} timeout={API_TIMEOUT}s")
            resp = await client.post(url, files=files, data=data, headers=headers, timeout=API_TIMEOUT)
            logger.info(f"[SCAN] ML responded status={resp.status_code}")
        if resp.status_code != 200:
            # Show error with navigation back to main menu
            keyboard = types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', user_language), callback_data='action_main_menu')]]
            )
            await progress_msg.edit_text(i18n.get_text('analysis_failed', user_language), reply_markup=keyboard)
            await state.clear()
            return
        result = resp.json()
        logger.info(f"[SCAN] ML JSON keys={list(result.keys()) if isinstance(result, dict) else type(result)}")
        # Perplexity endpoint returns { language, analysis }
        analysis = result.get('analysis') or {}
        if analysis:
            tn = analysis.get('total_nutrition', {})
            prov = analysis.get('provenance', {}) if isinstance(analysis, dict) else {}
            # Save per-100g for portion calc if available
            per100 = prov.get('per_100g', {})
            product_name = analysis.get('food_items', [{}])[0].get('name', 'Product')
            await state.update_data(per100=per100, product_name=product_name, user_db_id=user['id'])
            # Rich product details from OFF when available
            title_line = product_name
            brand = prov.get('brand')
            if brand:
                title_line = f"{product_name} — {brand}"
            nova = prov.get('nova_group')
            nutri = prov.get('nutriscore_grade')
            serving = prov.get('serving_size') or '100g'
            # Extra product fields for richer details
            quantity = prov.get('quantity')
            labels = prov.get('labels')
            countries = prov.get('countries')
            categories = prov.get('categories') or ''
            allergens = ', '.join(prov.get('allergens', []) or [])
            additives = ', '.join(prov.get('additives', []) or [])

            extra_lines = []
            if nova or nutri:
                extra_lines.append(f"🏷 NOVA: {nova or '-'} · Nutri-Score: {nutri or '-'}")
            # Serving label localized
            extra_lines.append(f"🍽 {i18n.get_text('serving_label', user_language, default='Serving')}: {serving}")
            if quantity:
                extra_lines.append(f"📦 Quantity: {quantity}")
            if labels:
                extra_lines.append(f"🏅 Labels: {labels}")
            if countries:
                extra_lines.append(f"🌍 Countries: {countries}")
            # Micronutrients if present
            if any(k in tn for k in ("saturated_fat","sugars","fiber","salt")):
                extra_lines.append(
                    f"🧪 sat. fat: {tn.get('saturated_fat','-')} g · sugars: {tn.get('sugars','-')} g · fiber: {tn.get('fiber','-')} g · salt: {tn.get('salt','-')} g"
                )
            if categories:
                extra_lines.append(f"🗂 {categories[:120]}" + ("…" if len(categories) > 120 else ""))
            if allergens:
                extra_lines.append(f"⚠️ Allergens: {allergens}")
            if additives:
                extra_lines.append(f"🧬 Additives: {additives}")

            # Add compact debug info if available
            debug_info = ""
            prov_debug = prov.get('debug') if isinstance(prov, dict) else None
            if prov_debug:
                dbg_lines = []
                if isinstance(prov_debug.get('barcodes_detected'), list):
                    dbg_lines.append(f"barcodes: {', '.join(map(str, prov_debug.get('barcodes_detected')))}")
                if 'time_ms' in prov_debug:
                    dbg_lines.append(f"time: {prov_debug.get('time_ms')} ms")
                if 'source' in prov:
                    dbg_lines.append(f"source: {prov.get('source')}")
                if dbg_lines:
                    debug_info = "\n\n<code>" + " | ".join(dbg_lines) + "</code>"

            # Enrich from Perplexity sections
            na = analysis.get('nutrition_analysis') or {}
            rec = analysis.get('recommendations') or {}
            positives = na.get('positive_aspects') or []
            improvements = na.get('improvement_suggestions') or []
            usage_tips = rec.get('usage_tips') or []
            alternatives = rec.get('better_alternatives') or []
            motivation = analysis.get('motivation_message') or ""

            # Suitability vs user profile
            profile = await get_user_profile(user['id'])
            suitability_lines = []
            suitability_ok = True
            if profile:
                diet = (profile.get('dietary_preferences') or [])
                allergies_list = (profile.get('allergies') or [])
                goal = profile.get('goal')
                name_low = (product_name or '').lower()
                cats = (categories or '').lower()
                is_dairy = any(k in (name_low + ' ' + cats) for k in ['сыр','молок','cheese','milk','dairy'])
                if is_dairy and ('dairy_free' in diet or 'без_молочного' in diet):
                    suitability_ok = False
                    suitability_lines.append('⚠️ Not suitable for your dairy-free diet')
                if any(a.lower() in (name_low + ' ' + cats) for a in allergies_list):
                    suitability_ok = False
                    suitability_lines.append('⚠️ May match your allergies')
                if goal == 'maintain_weight' and float(tn.get('calories') or 0) >= 300:
                    suitability_lines.append('ℹ️ Energy-dense; keep portions modest')

            fats_val = float(tn.get('fats') or 0)
            calories_val = float(tn.get('calories') or 0)
            carbs_val = float(tn.get('carbohydrates') or 0)
            best_time = ('Обед или ранний ужин' if fats_val >= 20 or calories_val >= 300 else ('Утро/после активности' if carbs_val >= 25 else 'Любое время')) if user_language == 'ru' else ('Lunch or early dinner' if fats_val >= 20 or calories_val >= 300 else ('Morning/after activity' if carbs_val >= 25 else 'Any time'))

            txt = (
                f"✅ {i18n.get_text('analysis_complete', user_language)}\n\n"
                f"<b>{title_line}</b>\n" + ("\n".join(extra_lines) + "\n\n" if extra_lines else "") +
                f"{i18n.get_text('total_nutrition', user_language)}\n"
                f"{i18n.get_text('calories_label', user_language)}: {tn.get('calories', '?')} {i18n.get_text('cal', user_language)}\n"
                f"{i18n.get_text('proteins_label', user_language)}: {tn.get('proteins', '?')} g\n"
                f"{i18n.get_text('fats_label', user_language)}: {tn.get('fats', '?')} g\n"
                f"{i18n.get_text('carbohydrates_label', user_language)}: {tn.get('carbohydrates', '?')} g" + debug_info + "\n\n"
            )
            if motivation:
                txt += motivation + "\n\n"
            if positives:
                txt += (('💚 Полезные стороны:' if user_language=='ru' else '💚 Positive aspects:') + "\n" + "\n".join([f"• {p}" for p in positives[:5]]) + "\n\n")
            if improvements:
                txt += (('⚠️ Нюансы/риски:' if user_language=='ru' else '⚠️ Caveats/Risks:') + "\n" + "\n".join([f"• {p}" for p in improvements[:5]]) + "\n\n")
            if usage_tips:
                txt += (('🧑‍🍳 Рекомендации по применению:' if user_language=='ru' else '🧑‍🍳 Usage tips:') + "\n" + "\n".join([f"• {t}" for t in usage_tips[:5]]) + "\n")
            txt += ("\n" + ("🕒 Лучшее время: " if user_language=='ru' else '🕒 Best time: ') + best_time + "\n\n")
            if alternatives:
                txt += (('🔁 Чем заменить:' if user_language=='ru' else '🔁 Alternatives:') + "\n" + "\n".join([f"• {a}" for a in alternatives[:5]]) + "\n\n")
            if profile:
                suit_header = '✅ Подходит вашему профилю' if suitability_ok else '⚠️ Может не подходить вашему профилю'
                suit_lines = "\n".join(suitability_lines) if suitability_lines else ''
                txt += suit_header + ("\n" + suit_lines if suit_lines else '') + "\n\n"
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text=i18n.get_text('ate_this_btn', user_language), callback_data='action_ate_this')],
                [types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', user_language), callback_data='action_main_menu')]
            ])
            await progress_msg.edit_text(txt, parse_mode='HTML', reply_markup=keyboard)
            return
        else:
            # Differentiate between: barcode detected but OFF has no product vs no barcode detected
            txt = i18n.get_text('scan_tips', user_language, default='Please try another photo of the label.')
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text=i18n.get_text('scan_try_again_btn', user_language, default='🔁 Try again'), callback_data='action_scan_again')],
                [types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', user_language), callback_data='action_main_menu')]
            ])
            await progress_msg.edit_text(txt, parse_mode='Markdown', reply_markup=keyboard)
            await state.clear()
    except Exception as e:
        logger.error(f"[SCAN] Error processing barcode photo: {repr(e)}")
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[[types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', 'ru'), callback_data='action_main_menu')]]
        )
        await message.answer(i18n.get_text('analysis_failed', 'ru'), reply_markup=keyboard)
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


