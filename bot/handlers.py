from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.api_client import fetch_data


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Guruhlar", callback_data="view_groups"),
         InlineKeyboardButton("O'qituvchilar", callback_data="view_teachers")],
        [InlineKeyboardButton("Xonalar", callback_data="view_rooms"),
         InlineKeyboardButton("Fanlar", callback_data="view_subjects")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Xush kelibsiz! Biror opsiyani tanlang:", reply_markup=reply_markup)


async def fetch_and_display_options(update, endpoint, prompt, callback_prefix):
    query = update.callback_query
    await query.answer()
    items = fetch_data(endpoint).get("results", [])

    keyboard = [
                   [InlineKeyboardButton(item.get("name", item.get("username", "Noma'lum")),
                                         callback_data=f"{callback_prefix}_{item['id']}")]
                   for item in items
               ] + [[InlineKeyboardButton("🔙 Orqaga", callback_data="go_back")]]

    await query.edit_message_text(prompt, reply_markup=InlineKeyboardMarkup(keyboard))


async def display_schedule(update, context):
    query = update.callback_query
    await query.answer()

    filter_type, filter_id = query.data.split("_")
    params = {filter_type: filter_id}
    schedules = fetch_data("schedules", params).get("results", [])

    if schedules:
        schedule_text = "\n\n".join(
            f"Kun: {s['day_of_week']}, Boshlanish: {s['start_time']}, Tugash: {s['end_time']}, Fan: {s['subject']}, Xona: {s['room']} ({s.get('room_number', 'N/A')}), Sessiya: {s['session_number']}"
            for s in schedules
        )
        await query.edit_message_text(f"Jadval:\n\n{schedule_text}")
    else:
        await query.edit_message_text("Bu tanlov uchun jadval mavjud emas.")


async def go_back(update, context):
    await start(update, context)