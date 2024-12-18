from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests
from config import BASE_URL


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Guruhlar", callback_data="view_groups"),
         InlineKeyboardButton("O'qituvchilar", callback_data="view_teachers")],
        [InlineKeyboardButton("Xonalar", callback_data="view_rooms"),
         InlineKeyboardButton("Fanlar", callback_data="view_subjects")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await (update.message.reply_text if update.message else update.callback_query.edit_message_text)(
        "Xush kelibsiz! Biror opsiyani tanlang:", reply_markup=reply_markup
    )


async def fetch_and_display_options(update, endpoint, prompt, callback_prefix):
    query = update.callback_query
    await query.answer()

    url = f"{BASE_URL}/{endpoint}/"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("results", [])
        field_map = {"teachers": "username", "groups": "name", "rooms": "name", "subjects": "name"}
        field = field_map.get(endpoint, "name")

        buttons = [
            InlineKeyboardButton(item.get(field, "Noma'lum"), callback_data=f"{callback_prefix}_{item['id']}")
            for item in items
        ]
        keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]  # 2 ustunli qilish

        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="go_back")])

        await query.edit_message_text(prompt, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text("Ma'lumotlarni yuklashda xatolik yuz berdi.")


async def display_schedule(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    filter_type, filter_id = query.data.split("_")
    url = f"{BASE_URL}/schedules/?{filter_type}={filter_id}"
    response = requests.get(url)
    if response.status_code == 200:
        schedules = response.json().get("results", [])
        if schedules:
            schedule_text = "\n\n".join(
                f"Kun: {schedule.get('day_of_week', 'Noma\'lum')}, "
                f"Boshlanish: {schedule.get('start_time', 'Noma\'lum')}, "
                f"Tugash: {schedule.get('end_time', 'Noma\'lum')}, "
                f"Fan: {schedule.get('subject', 'Noma\'lum')}, "
                f"Xona: {schedule.get('room', 'Noma\'lum')} "
                f"(Xona raqami: {schedule.get('room_number', 'N/A')}), "
                f"Sessiya: {schedule.get('session_number', 'Noma\'lum')}"
                for schedule in schedules
            )
            await query.edit_message_text(f"Jadval:\n\n{schedule_text}", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Orqaga", callback_data="go_back")]]
            ))
        else:
            await query.edit_message_text("Bu filtrlash uchun jadval topilmadi.")
    else:
        await query.edit_message_text("Jadvalni olishda xatolik yuz berdi.")


async def get_groups(update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, "groups", "Guruhni tanlang:", "group")


async def get_teachers(update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, "teachers", "O'qituvchini tanlang:", "teacher")


async def get_rooms(update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, "rooms", "Xonani tanlang:", "room")


async def get_subjects(update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, "subjects", "Fanni tanlang:", "subject")


async def go_back(update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
