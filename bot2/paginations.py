from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests
from bot2.handlers import fetch_and_display_options


async def paginate(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        _, endpoint, direction = query.data.split("_")
    except ValueError:
        await query.edit_message_text("Xatolik yuz berdi. Tugma ma'lumotlari noto‘g‘ri.")
        return

    # Fetch the correct page URL
    current_url = context.user_data.get(f"{endpoint}_{direction}")
    if not current_url:
        await query.edit_message_text("Sahifa ma'lumotlari mavjud emas.")
        return

    # Immediately transition to fetch_and_display_options
    await fetch_and_display_options(
        update=update,
        context=context,
        endpoint=endpoint,
        prompt=f"{endpoint.capitalize()} tanlang:",
        callback_prefix=f"view_{endpoint}",
        page_url=current_url,
    )






async def paginate_schedules(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    direction = query.data.split("_")[1]
    current_url = context.user_data.get(f"schedules_{direction}")

    if not current_url:
        await query.edit_message_text("Sahifa ma'lumotlari mavjud emas.1")
        return

    response = requests.get(current_url)
    if response.status_code == 200:
        data = response.json()
        context.user_data[f"schedules_next"] = data.get("next", None)
        context.user_data[f"schedules_previous"] = data.get("previous", None)
        schedules = data.get("results", [])

        if schedules:
            schedule_text = "\n\n".join(
                f"📅 Kun: {schedule.get('day_of_week', 'Noma\'lum')}\n"
                f"⏰ Boshlanish: {schedule.get('start_time', 'Noma\'lum')} | "
                f"Tugash: {schedule.get('end_time', 'Noma\'lum')}\n"
                f"👥 Guruh: {', '.join(group.get('name', 'Noma\'lum') for group in schedule.get('group', []))}\n"
                f"📚 Fan: {schedule.get('subject', 'Noma\'lum')}\n"
                f"🏫 Xona: {schedule.get('room', 'Noma\'lum')} | "
                f"Raqam: {schedule.get('room_number', 'N/A')}\n"
                f"👨‍🏫 Ustoz: {schedule.get('teacher', 'Noma\'lum')}\n"
                f"🔢 Sessiya: {schedule.get('session_number', 'Noma\'lum')}"
                for schedule in schedules
            )

            pagination_buttons = []
            if data.get("previous"):
                pagination_buttons.append(InlineKeyboardButton("⬅ Oldingisi", callback_data="schedules_previous"))
            if data.get("next"):
                pagination_buttons.append(InlineKeyboardButton("Keyingisi ➡", callback_data="schedules_next"))

            keyboard = []
            if pagination_buttons:
                keyboard.append(pagination_buttons)
            keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="go_back")])

            await query.edit_message_text(f"Jadval:\n\n{schedule_text}", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text("Bu sahifada jadval topilmadi.")
    else:
        await query.edit_message_text("Jadvalni yuklashda xatolik yuz berdi.")


async def paginate_attendance(update, context):
    query = update.callback_query
    direction = query.data.split("_")[1]
    page_url = context.user_data.get(f"attendance_{direction}_page")


    if not page_url:
        await query.answer("Sahifa ma'lumotlari mavjud emas.")
        return

    access_token = context.user_data.get("access_token", None)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(page_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        schedules = data.get("results", [])
        next_page = data.get("next", None)
        previous_page = data.get("previous", None)

        context.user_data["attendance_next_page"] = next_page
        context.user_data["attendance_previous_page"] = previous_page

        schedule_text = "\n\n".join(
            f"{idx + 1}. 📅 Kun: {schedule.get('day_of_week', 'Noma\'lum')}\n"
            f"    🕒 Vaqt: {schedule.get('start_time', 'Noma\'lum')} - {schedule.get('end_time', 'Noma\'lum')}\n"
            f"    🎓 Fan: {schedule.get('subject', 'Noma\'lum')}\n"
            f"    🏫 Xona: {schedule.get('room', 'Noma\'lum')} ({schedule.get('room_number', 'N/A')})\n"
            f"    👥 Guruh: {', '.join(group.get('name', 'Noma\'lum') for group in schedule.get('group', []))}"
            for idx, schedule in enumerate(schedules)
        )

        schedule_buttons = [
            InlineKeyboardButton(f"{idx + 1}", callback_data=f"schedule_{schedule['id']}")
            for idx, schedule in enumerate(schedules)
        ]
        formatted_buttons = [schedule_buttons[i:i + 4] for i in range(0, len(schedule_buttons), 4)]

        pagination_buttons = []
        if previous_page:
            pagination_buttons.append(InlineKeyboardButton("⬅ Oldingisi", callback_data="attendance_previous"))
        pagination_buttons.append(InlineKeyboardButton("❌ Orqaga", callback_data="go_back"))
        if next_page:
            pagination_buttons.append(InlineKeyboardButton("Keyingisi ➡", callback_data="attendance_next"))

        formatted_buttons.append(pagination_buttons)

        reply_markup = InlineKeyboardMarkup(formatted_buttons)
        await query.edit_message_text(f"Davomat sahifalari:\n\n{schedule_text}", reply_markup=reply_markup)
    else:
        await query.edit_message_text("Davomatni olishda xatolik yuz berdi.")
