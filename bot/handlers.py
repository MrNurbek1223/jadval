import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import BASE_URL


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("View Groups", callback_data="view_groups")],
        [InlineKeyboardButton("View Teachers", callback_data="view_teachers")],
        [InlineKeyboardButton("View Rooms", callback_data="view_rooms")],
        [InlineKeyboardButton("View Subjects", callback_data="view_subjects")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.edit_message_text("Welcome! Choose an option:", reply_markup=reply_markup)


async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


async def get_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, "groups", "Select a group", "group")


async def get_teachers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, "teachers", "Select a teacher", "teacher")


async def get_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, "rooms", "Select a room", "room")


async def get_subjects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, "subjects", "Select a subject", "subject")


async def fetch_and_display_options(update: Update, endpoint: str, prompt: str, callback_prefix: str):
    query = update.callback_query
    await query.answer()

    try:
        response = requests.get(f"{BASE_URL}/{endpoint}/")
        response.raise_for_status()
        items = response.json()

        keyboard = [
            [InlineKeyboardButton(
                item.get("name", item.get("username", "Unnamed")),
                callback_data=f"{callback_prefix}_{item['id']}"
            )] for item in items
        ]
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="go_back")])

        await query.edit_message_text(prompt, reply_markup=InlineKeyboardMarkup(keyboard)) if items else \
            await query.edit_message_text(f"No {endpoint} available.")

    except requests.RequestException:
        await query.edit_message_text(f"Failed to retrieve {endpoint}. Try again later.")


async def display_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    filter_type, filter_id = query.data.split("_")
    url = f"{BASE_URL}/schedules/?{filter_type}={filter_id}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        schedules = response.json().get("results", [])

        if schedules:
            schedule_text = "\n\n".join(
                f"Day: {schedule['day_of_week']}, Start: {schedule['start_time']}, "
                f"End: {schedule['end_time']}, Subject: {schedule['subject']}, "
                f"Room: {schedule['room']}, Session: {schedule['session_number']}"
                for schedule in schedules
            )
            await query.edit_message_text(f"Schedule:\n\n{schedule_text}")
        else:
            await query.edit_message_text("No schedules found for this selection.")
    except requests.RequestException:
        await query.edit_message_text("Failed to retrieve schedule. Try again later.")
