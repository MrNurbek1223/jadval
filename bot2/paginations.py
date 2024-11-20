from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests

from bot2.handlers import fetch_and_display_options


async def paginate(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, endpoint, direction = query.data.split("_")
    current_url = context.user_data.get(f"{endpoint}_{direction}")

    if not current_url:
        await query.edit_message_text("Sahifa ma'lumotlari mavjud emas.")
        return

    response = requests.get(current_url)
    if response.status_code == 200:
        data = response.json()
        next_page = data.get("next", None)
        previous_page = data.get("previous", None)

        if next_page:
            context.user_data[f"{endpoint}_next"] = next_page
        if previous_page:
            context.user_data[f"{endpoint}_previous"] = previous_page

        await fetch_and_display_options(update, context, endpoint, f"{endpoint.capitalize()} tanlang:", endpoint,
                                        page_url=current_url)
    else:
        await query.edit_message_text("Xatolik yuz berdi. Ma'lumotlarni yuklab bo'lmadi.")


async def paginate_schedules(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    direction = query.data.split("_")[1]
    current_url = context.user_data.get(f"schedules_{direction}")

    if not current_url:
        await query.edit_message_text("Sahifa ma'lumotlari mavjud emas.")
        return

    response = requests.get(current_url)
    if response.status_code == 200:
        data = response.json()
        context.user_data[f"schedules_next"] = data.get("next", None)
        context.user_data[f"schedules_previous"] = data.get("previous", None)
        schedules = data.get("results", [])

        if schedules:
            schedule_text = "\n\n".join(
                f"Kun: {schedule.get('day_of_week', 'Noma\'lum')}\n"
                f"Boshlanish: {schedule.get('start_time', 'Noma\'lum')}\n"
                f"Tugash: {schedule.get('end_time', 'Noma\'lum')}\n"
                f"Fan: {schedule.get('subject', 'Noma\'lum')}\n"
                f"Xona: {schedule.get('room', 'Noma\'lum')}\n"
                f"Ustoz: {schedule.get('teacher', 'Noma\'lum')}\n"
                f"(Xona raqami: {schedule.get('room_number', 'N/A')})\n"
                f"Sessiya: {schedule.get('session_number', 'Noma\'lum')}"
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

