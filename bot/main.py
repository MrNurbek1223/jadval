from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from config import TOKEN
from handlers import start, get_groups, get_teachers, get_rooms, get_subjects, display_schedule, go_back



def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(get_groups, pattern="^view_groups$"))
    app.add_handler(CallbackQueryHandler(get_teachers, pattern="^view_teachers$"))
    app.add_handler(CallbackQueryHandler(get_rooms, pattern="^view_rooms$"))
    app.add_handler(CallbackQueryHandler(get_subjects, pattern="^view_subjects$"))
    app.add_handler(CallbackQueryHandler(display_schedule, pattern="^(group|teacher|room|subject)_"))
    app.add_handler(CallbackQueryHandler(go_back, pattern="^go_back$"))
    app.run_polling()

if __name__ == "__main__":
    main()