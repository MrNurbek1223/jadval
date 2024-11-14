import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.api_client import fetch_data


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Guruhlarni ko'rish", callback_data="view_groups")],
        [InlineKeyboardButton("O'qituvchilarni ko'rish", callback_data="view_teachers")],
        [InlineKeyboardButton("Xonalarni ko'rish", callback_data="view_rooms")],
        [InlineKeyboardButton("Fanlarni ko'rish", callback_data="view_subjects")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Xush kelibsiz! Biror opsiyani tanlang:", reply_markup=reply_markup)


async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


async def fetch_and_display_options(update: Update, endpoint, prompt, callback_prefix):
    query = update.callback_query
    await query.answer()

    items = fetch_data(endpoint)
    if items:
        keyboard = [
            [InlineKeyboardButton(item.get("name", item.get("username", "Noma'lum")),
                                  callback_data=f"{callback_prefix}_{item['id']}")]
            for item in items
        ]
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="go_back")])
        await query.edit_message_text(prompt, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text(f"{endpoint} mavjud emas.")


async def display_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    filter_type, filter_id = query.data.split("_")
    params = {filter_type: filter_id}
    schedules = fetch_data("schedules", params).get("results", [])

    if schedules:
        schedule_text = "\n\n".join(
            f"Kun: {schedule['day_of_week']}, Boshlanish: {schedule['start_time']}, "
            f"Tugash: {schedule['end_time']}, Fan: {schedule['subject']}, "
            f"Xona: {schedule['room']} (Xona raqami: {schedule.get('room_number', 'N/A')}), "
            f"Sessiya: {schedule['session_number']}"
            for schedule in schedules
        )
        await query.edit_message_text(f"Jadval:\n\n{schedule_text}")
    else:
        await query.edit_message_text("Bu tanlov uchun jadval mavjud emas.")


async def get_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, "groups", "Guruhni tanlang:", "group")


async def get_teachers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, "teachers", "O'qituvchini tanlang:", "teacher")


async def get_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, "rooms", "Xonani tanlang:", "room")


async def get_subjects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, "subjects", "Fanni tanlang:", "subject")
