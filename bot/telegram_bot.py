import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes


TOKEN = '7808237529:AAEE_CD8eLKpoPOuVREfgQuBMg7xWqmmzIw'
BASE_URL = "http://127.0.0.1:8000"  # Django API's base URL


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("View Groups", callback_data="view_groups")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Choose an option:", reply_markup=reply_markup)

async def get_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        response = requests.get(f"{BASE_URL}/groups/")
        response.raise_for_status()
        groups = response.json()
        if groups:
            keyboard = [[InlineKeyboardButton(group["name"], callback_data=f"group_{group['id']}")] for group in groups]
            await query.edit_message_text("Select a group:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text("No groups available.")
    except requests.RequestException:
        await query.edit_message_text("Failed to retrieve groups. Try again later.")

async def display_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    group_id = query.data.split("_")[1]
    try:
        response = requests.get(f"{BASE_URL}/schedules/?group={group_id}")
        response.raise_for_status()
        schedules = response.json().get("results", [])
        if schedules:
            schedule_text = "\n\n".join(
                f"Day: {schedule['day_of_week']}, Start: {schedule['start_time']}, End: {schedule['end_time']}, "
                f"Subject: {schedule['subject']}, Room: {schedule['room']}, Session: {schedule['session_number']}"
                for schedule in schedules
            )
            await query.edit_message_text(f"Group {group_id} Schedule:\n\n{schedule_text}")
        else:
            await query.edit_message_text("No schedules found for this group.")
    except requests.RequestException:
        await query.edit_message_text("Failed to retrieve schedule. Try again later.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(get_groups, pattern="^view_groups$"))
    app.add_handler(CallbackQueryHandler(display_schedule, pattern="^group_"))
    app.run_polling()

if __name__ == "__main__":
    main()