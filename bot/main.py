from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import TOKEN
from handlers import start, display_schedule, go_back, fetch_and_display_options


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(lambda u, c: fetch_and_display_options(u, "groups", "Guruhni tanlang:", "group"), pattern="^view_groups$"))
    app.add_handler(CallbackQueryHandler(lambda u, c: fetch_and_display_options(u, "teachers", "O'qituvchini tanlang:", "teacher"), pattern="^view_teachers$"))
    app.add_handler(CallbackQueryHandler(lambda u, c: fetch_and_display_options(u, "rooms", "Xonani tanlang:", "room"), pattern="^view_rooms$"))
    app.add_handler(CallbackQueryHandler(lambda u, c: fetch_and_display_options(u, "subjects", "Fanni tanlang:", "subject"), pattern="^view_subjects$"))
    app.add_handler(CallbackQueryHandler(display_schedule, pattern="^(group|teacher|room|subject)_"))
    app.add_handler(CallbackQueryHandler(go_back, pattern="^go_back$"))

    app.run_polling()

if __name__ == "__main__":
    main()