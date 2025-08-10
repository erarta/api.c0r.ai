import os
import httpx
import math
import re
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger
from i18n.i18n import i18n
from common.supabase_client import get_or_create_user
from common.db.profiles import get_user_profile

ML_SERVICE_URL = os.getenv("ML_SERVICE_URL")
# Perplexity label analysis can be slow under load; keep generous timeout after we already sent a progress message
API_TIMEOUT = 45.0


class ScanStates(StatesGroup):
    waiting_for_photo = State()
    waiting_for_grams = State()


def _is_generic_points(points: list[str] | None, user_language: str) -> bool:
    if not points:
        return True
    # If Russian UI but bullets look like short English clichés, treat as generic
    if user_language == 'ru':
        joined = ' '.join(points)
        only_ascii = re.fullmatch(r"[\x00-\x7F\s.,!?'\-:;()]+", joined or '') is not None
        too_short = len(points) <= 1 and len(points[0]) <= 20
        common = any(p.strip().lower() in {'nutritious meal', 'healthy choice', 'add more vegetables'} for p in points)
        return only_ascii or too_short or common
    # For EN, consider generic if extremely short
    return len(points) == 1 and len(points[0]) < 16


def _generate_personalized_points(total_nutrition: dict, profile: dict | None, user_language: str) -> tuple[list[str], list[str]]:
    """Create meaningful positives/improvements from nutrition + profile."""
    def t(ru: str, en: str) -> str:
        return ru if user_language == 'ru' else en

    def to_float(v) -> float:
        try:
            return float(v)
        except Exception:
            return 0.0

    cals = to_float(total_nutrition.get('calories'))
    prot = to_float(total_nutrition.get('proteins'))
    fats = to_float(total_nutrition.get('fats'))
    carbs = to_float(total_nutrition.get('carbohydrates'))
    sugar = to_float(total_nutrition.get('sugars'))
    fiber = to_float(total_nutrition.get('fiber'))
    salt = to_float(total_nutrition.get('salt'))
    sat_fat = to_float(total_nutrition.get('saturated_fat'))

    goal = (profile or {}).get('goal') if profile else None
    diet = (profile or {}).get('dietary_preferences') or []

    positives: list[str] = []
    improvements: list[str] = []

    # Positives
    if prot >= 12:
        positives.append(t('Хороший источник белка — поможет сытости и восстановлению', 'Good protein source — supports satiety and recovery'))
    if fiber >= 3:
        positives.append(t('Достаточно клетчатки — полезно для пищеварения', 'Good fiber — supports digestion'))
    if sugar > 0 and sugar <= 5:
        positives.append(t('Низкое содержание сахара', 'Low in sugar'))
    if salt > 0 and salt <= 0.3:
        positives.append(t('Низкое содержание соли', 'Low in salt'))
    if cals <= 120:
        positives.append(t('Низкая калорийность на 100 г — удобно для контроля веса', 'Low calories per 100 g — helpful for weight control'))
    if 8 <= fats <= 18 and 10 <= prot <= 25 and 5 <= carbs <= 25:
        positives.append(t('Сбалансированные макроэлементы', 'Balanced macros'))

    # Improvements (actionable, not generic)
    if sat_fat >= 10 or fats >= 20:
        improvements.append(t('Контролируй размер порции: продукт достаточно жирный', 'Watch portion size: product is quite fatty'))
    if salt >= 1.5:
        improvements.append(t('Соль выше нормы — по возможности выбирай вариант с меньшим содержанием соли', 'High salt — consider a lower-salt option'))
    if fiber < 3:
        improvements.append(t('Добавь овощи/зелень для клетчатки и микронутриентов', 'Add vegetables/greens for fiber and micronutrients'))
    if goal == 'gain_weight' and cals < 180:
        improvements.append(t('Для набора веса добавь источник сложных углеводов (крупы/хлеб цельнозерновой)', 'For weight gain, add complex carbs (grains/wholegrain bread)'))
    if goal == 'lose_weight' and cals >= 250:
        improvements.append(t('При похудении выбирай меньшую порцию или менее калорийную альтернативу', 'If losing weight, choose smaller portion or a lighter alternative'))

    # Deduplicate and keep top 3 each
    def dedup(items: list[str]) -> list[str]:
        seen = set()
        out = []
        for it in items:
            key = it.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(it)
        return out[:3]

    return dedup(positives), dedup(improvements)

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
        # Pass Telegram ID to ML so it can fetch full user context (diet, allergies, goal, daily target)
        headers["X-Telegram-Id"] = str(telegram_user_id)
        if 'Content-Type' in headers:
            del headers['Content-Type']
        async with httpx.AsyncClient() as client:
            # Switch to Perplexity-based label analysis for richer results
            url = f"{ML_SERVICE_URL}/api/v1/label/perplexity"
            logger.info(f"[SCAN] POST {url} timeout={API_TIMEOUT}s")
            try:
                resp = await client.post(url, files=files, data=data, headers=headers, timeout=API_TIMEOUT)
            except httpx.ReadTimeout:
                logger.error("[SCAN] ML request timed out")
                keyboard = types.InlineKeyboardMarkup(
                    inline_keyboard=[
                        [types.InlineKeyboardButton(text=i18n.get_text('scan_try_again_btn', user_language, default='🔁 Try again'), callback_data='action_scan_again')],
                        [types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', user_language), callback_data='action_main_menu')]
                    ]
                )
                await progress_msg.edit_text(i18n.get_text('analysis_failed', user_language), reply_markup=keyboard)
                await state.clear()
                return
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

            # Add compact debug info if available (hide 'source'; localize barcode label)
            debug_info = ""
            prov_debug = prov.get('debug') if isinstance(prov, dict) else None
            if prov_debug:
                dbg_lines = []
                if isinstance(prov_debug.get('barcodes_detected'), list):
                    barcode_label = 'Штрих‑код' if user_language == 'ru' else 'Barcode'
                    dbg_lines.append(f"{barcode_label}: {', '.join(map(str, prov_debug.get('barcodes_detected')))}")
                if 'time_ms' in prov_debug:
                    dbg_lines.append(f"time: {prov_debug.get('time_ms')} ms")
                # deliberately not showing 'source'
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
                    suitability_lines.append('⚠️ ' + ("В профиле указано исключать молочное — продукт может не подходить" if user_language=='ru' else "You exclude dairy in profile — product may not be suitable"))
                if any(a.lower() in (name_low + ' ' + cats) for a in allergies_list):
                    suitability_ok = False
                    suitability_lines.append('⚠️ ' + ("Найдены совпадения с вашими аллергиями" if user_language=='ru' else "May match your allergies"))
                if goal == 'maintain_weight' and float(tn.get('calories') or 0) >= 300:
                    suitability_lines.append('ℹ️ ' + ("Продукт калориен — держите порцию небольшой" if user_language=='ru' else "Energy-dense; keep portions modest"))

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
            # Replace generic LLM bullets with personalized ones if needed
            if _is_generic_points(positives, user_language) or _is_generic_points(improvements, user_language):
                gen_pos, gen_imp = _generate_personalized_points(tn, profile, user_language)
                if gen_pos:
                    positives = gen_pos
                if gen_imp:
                    improvements = gen_imp
            if positives:
                header = ('💪 Что хорошо в этом продукте:' if user_language=='ru' else "💚 What's good:")
                txt += (header + "\n" + "\n".join([f"• {p}" for p in positives[:5]]) + "\n\n")
            if improvements:
                header = ('💡 Как улучшить это:' if user_language=='ru' else '💡 How to improve:')
                txt += (header + "\n" + "\n".join([f"• {p}" for p in improvements[:5]]) + "\n\n")
            if usage_tips:
                header = ('🧑‍🍳 Советы по использованию:' if user_language=='ru' else '🧑‍🍳 Usage tips:')
                txt += (header + "\n" + "\n".join([f"• {t}" for t in usage_tips[:5]]) + "\n")
            txt += ("\n" + ("🕒 Лучшее время: " if user_language=='ru' else '🕒 Best time: ') + best_time + "\n\n")
            if alternatives:
                txt += (("🔁 Чем заменить:" if user_language=='ru' else '🔁 Alternatives:') + "\n" + "\n".join([f"• {a}" for a in alternatives[:5]]) + "\n\n")
            # Personalized block
            personal_lines = []
            if profile:
                suit_header = '✅ Подходит вашему профилю' if suitability_ok else '⚠️ Может не подходить вашему профилю'
                suit_lines = "\n".join(suitability_lines) if suitability_lines else ''
                txt += suit_header + ("\n" + suit_lines if suit_lines else '') + "\n\n"
                # Daily target line
                daily_target = profile.get('daily_calories_target')
                if daily_target:
                    personal_lines.append(('🎯 Дневная цель: ' if user_language=='ru' else '🎯 Daily target: ') + f"{daily_target} " + i18n.get_text('cal', user_language))
                # Goal tip
                goal = profile.get('goal')
                if goal == 'lose_weight':
                    personal_lines.append(i18n.get_text('rec_lose_weight', user_language, default=''))
                elif goal == 'gain_weight':
                    personal_lines.append(i18n.get_text('rec_gain_weight', user_language, default=''))
                elif goal == 'maintain_weight':
                    personal_lines.append(i18n.get_text('rec_maintain_weight', user_language, default=''))
            # Portion specific tip for very caloric items
            if calories_val >= 300 or fats_val >= 20:
                personal_lines.append('🥄 ' + ("Рекомендуемая порция ≤ 100 г" if user_language=='ru' else "Suggested portion ≤ 100 g"))

            if personal_lines:
                txt += (('🧭 Персональные рекомендации:\n' if user_language=='ru' else '🧭 Personalized recommendations:\n') + "\n".join([ln for ln in personal_lines if ln]) + "\n\n")
            # Build keyboard (OpenFoodFacts removed)
            kb_rows = [[types.InlineKeyboardButton(text=i18n.get_text('ate_this_btn', user_language), callback_data='action_ate_this')]]
            kb_rows.append([types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', user_language), callback_data='action_main_menu')])
            keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb_rows)
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
        # Build informative confirmation with delta and new daily total
        try:
            from common.calories_manager import get_daily_calories
            daily = get_daily_calories(user_db_id)
            total_today = daily.get('total_calories')
        except Exception:
            total_today = None

        if user_language == 'ru':
            added_line = f"✅ Добавлено в дневной итог: {round(cals,1)} ккал (Б {round(prot,1)} • Ж {round(fats,1)} • У {round(carbs,1)})"
            total_line = f"Сегодня всего: {round(total_today,1)} ккал" if total_today is not None else ""
            confirm_text = added_line + ("\n" + total_line if total_line else "")
        else:
            added_line = f"✅ Added to daily total: {round(cals,1)} kcal (P {round(prot,1)} • F {round(fats,1)} • C {round(carbs,1)})"
            total_line = f"Today's total: {round(total_today,1)} kcal" if total_today is not None else ""
            confirm_text = added_line + ("\n" + total_line if total_line else "")

        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text=("📅 Мой день" if user_language=='ru' else "📅 My day"), callback_data='action_daily')],
            [types.InlineKeyboardButton(text=("📦 Сканировать ещё" if user_language=='ru' else "📦 Scan another"), callback_data='action_scan_again')],
            [types.InlineKeyboardButton(text=i18n.get_text('btn_main_menu', user_language), callback_data='action_main_menu')],
        ])

        await message.answer(confirm_text, parse_mode='HTML', reply_markup=kb)
        await state.clear()
    except Exception as e:
        logger.error(f"Error in process_portion_grams: {e}")
        await message.answer(i18n.get_text('error_general', 'en'))
        await state.clear()


async def handle_off_search(callback: types.CallbackQuery, state: FSMContext):
    # OpenFoodFacts functionality removed
    await callback.answer()
    user = await get_or_create_user(callback.from_user.id)
    language = user.get('language', 'en') if user else 'en'
    await callback.message.answer(i18n.get_text('error_generic', language))

