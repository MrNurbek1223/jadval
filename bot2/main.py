from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from bot2.paginations import paginate_schedules, paginate_attendance
from bot2.search import handle_search_query, search_handler, clear_search_handler
from config import TOKEN
from handlers import start, display_schedule, get_groups, get_teachers, get_rooms, get_subject, go_back, view_schedule, \
    attendance_handler, handle_login_credentials, confirm_attendance, toggle_student, \
    get_schedule_groups, get_group_students, paginate, unified_text_handler, do_attendance, view_attendance, \
    view_group_attendance, view_student_attendance, paginate_groups, \
    view_subject_attendance, view_groups, view_subjects, paginate_subjects, view_group_statistics, \
    fetch_group_statistics, paginate_group_stats


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_login_credentials))
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unified_text_handler))

    app.add_handler(CallbackQueryHandler(start, pattern="^go_back_to_start$"))
    app.add_handler(CallbackQueryHandler(view_schedule, pattern="^view_schedule$"))
    app.add_handler(CallbackQueryHandler(get_groups, pattern="^view_groups"))
    app.add_handler(CallbackQueryHandler(get_teachers, pattern="^view_teachers"))
    app.add_handler(CallbackQueryHandler(get_rooms, pattern="^view_rooms"))
    app.add_handler(CallbackQueryHandler(get_subject, pattern="^view_subject"))
    app.add_handler(CallbackQueryHandler(paginate_schedules, pattern="^schedules_(next|previous)$"))
    app.add_handler(CallbackQueryHandler(paginate_attendance, pattern="^attendance_(next|previous)$"))
    app.add_handler(CallbackQueryHandler(display_schedule, pattern="^(group|teacher|room|subject)_"))
    app.add_handler(CallbackQueryHandler(go_back, pattern="^go_back$"))
    app.add_handler(
        CallbackQueryHandler(paginate, pattern="^paginate_(teachers|groups|rooms|subject)_(next|previous)$"))
    app.add_handler(CallbackQueryHandler(attendance_handler, pattern="^attendance$"))


    app.add_handler(CallbackQueryHandler(search_handler, pattern="^search_(groups|teachers|rooms|subject)$"))
    app.add_handler(
        CallbackQueryHandler(clear_search_handler, pattern="^clear_search_(groups|teachers|rooms|subject)$"))
    app.add_handler(
        CallbackQueryHandler(paginate, pattern="^paginate_(groups|teachers|rooms|subject)_(next|previous)$"))

    app.add_handler(CallbackQueryHandler(get_schedule_groups, pattern="^schedule_"))
    app.add_handler(CallbackQueryHandler(get_group_students, pattern="^attendance_group_"))
    app.add_handler(CallbackQueryHandler(toggle_student, pattern="^toggle_"))
    app.add_handler(CallbackQueryHandler(confirm_attendance, pattern="^confirm_attendance$"))

    app.add_handler(CallbackQueryHandler(do_attendance, pattern="^do_attendance$"))

    app.add_handler(CallbackQueryHandler(view_attendance, pattern="^view_attendance$"))
    app.add_handler(CallbackQueryHandler(view_groups, pattern="^attendance_view_groups$"))
    app.add_handler(CallbackQueryHandler(view_subjects, pattern="^attendance_view_subjects$"))
    app.add_handler(CallbackQueryHandler(view_group_attendance, pattern="^attendance_group1_"))
    app.add_handler(CallbackQueryHandler(view_subject_attendance, pattern="^attendance_subject_"))


    app.add_handler(CallbackQueryHandler(paginate_groups, pattern="^paginate1_groups_(previous|next)$"))
    app.add_handler(CallbackQueryHandler(paginate_subjects, pattern="^paginate2_subjects_(previous|next)$"))

    app.add_handler(CallbackQueryHandler(view_group_statistics, pattern="^view_group0_statistics$"))
    app.add_handler(CallbackQueryHandler(fetch_group_statistics, pattern="^group0_stats_"))
    app.add_handler(CallbackQueryHandler(paginate_group_stats, pattern="^paginate_group_stats_(previous|next)$"))

    app.run_polling()


if __name__ == "__main__":
    main()
