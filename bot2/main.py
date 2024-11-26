from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler ,MessageHandler, filters
from bot2.paginations import paginate_schedules, paginate, paginate_attendance
from config import TOKEN
from handlers import start, display_schedule, get_groups, get_teachers, get_rooms, get_subject, go_back, view_schedule, \
    attendance_handler, handle_login_credentials, confirm_attendance, toggle_student, \
    get_schedule_groups, get_group_students


def main():

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))



    app.add_handler(CallbackQueryHandler(start, pattern="^go_back_to_start$"))
    app.add_handler(CallbackQueryHandler(view_schedule, pattern="^view_schedule$"))
    app.add_handler(CallbackQueryHandler(get_groups, pattern="^view_groups"))
    app.add_handler(CallbackQueryHandler(get_teachers, pattern="^view_teachers"))
    app.add_handler(CallbackQueryHandler(get_rooms, pattern="^view_rooms"))
    app.add_handler(CallbackQueryHandler(paginate_schedules, pattern="^schedules_(next|previous)$"))
    app.add_handler(CallbackQueryHandler(paginate_attendance, pattern="^attendance_(next|previous)$"))
    app.add_handler(CallbackQueryHandler(get_subject, pattern="^view_subject"))
    app.add_handler(CallbackQueryHandler(display_schedule, pattern="^(group|teacher|room|subject)_"))
    app.add_handler(CallbackQueryHandler(go_back, pattern="^go_back$"))
    app.add_handler(CallbackQueryHandler(paginate, pattern="^paginate_.*"))
    app.add_handler(CallbackQueryHandler(attendance_handler, pattern="^attendance$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_login_credentials))

    app.add_handler(CallbackQueryHandler(get_schedule_groups, pattern="^schedule_"))
    app.add_handler(CallbackQueryHandler(get_group_students, pattern="^attendance_group_"))


    app.add_handler(CallbackQueryHandler(toggle_student, pattern="^toggle_"))
    app.add_handler(CallbackQueryHandler(confirm_attendance, pattern="^confirm_attendance$"))



    app.run_polling()


if __name__ == "__main__":
    main()
