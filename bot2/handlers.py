from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests
from config import BASE_URL, SCHEDULES_URL, LOGIN_URL


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Davomat qilish", callback_data="attendance"),
         InlineKeyboardButton("Dars jadvali", callback_data="view_schedule")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await (update.message.reply_text if update.message else update.callback_query.edit_message_text)(
        "Xush kelibsiz! Quyidagi opsiyalardan birini tanlang:", reply_markup=reply_markup
    )


async def view_schedule(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Guruhlar", callback_data="view_groups"),
         InlineKeyboardButton("O'qituvchilar", callback_data="view_teachers")],
        [InlineKeyboardButton("Xonalar", callback_data="view_rooms"),
         InlineKeyboardButton("Fanlar", callback_data="view_subject")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="go_back_to_start")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Dars jadvali bo'yicha opsiyalardan birini tanlang:", reply_markup=reply_markup)


async def attendance_handler(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("Iltimos, email va parolingizni kiriting:\nFormat: email password")

    context.user_data["waiting_for_login"] = True


async def handle_login_credentials(update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_for_login"):
        user_input = update.message.text.split()
        if len(user_input) != 2:
            await update.message.reply_text("Noto‘g‘ri format. Iltimos, email va parolni qaytadan kiriting.")
            return
        email, password = user_input

        response = requests.post(LOGIN_URL, json={"email": email, "password": password})
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access", None)

            if access_token:
                context.user_data["access_token"] = access_token
                await update.message.reply_text("Login muvaffaqiyatli amalga oshirildi. Dars jadvalini yuklayapman...")
                await get_teacher_schedule(update, context)
            else:
                await update.message.reply_text("Login amalga oshirilmadi. Iltimos, qayta urinib ko‘ring.")
        else:
            await update.message.reply_text("Login xatolik yuz berdi. Iltimos, qayta urinib ko‘ring.")

        context.user_data["waiting_for_login"] = False


async def get_teacher_schedule(update, context: ContextTypes.DEFAULT_TYPE):
    access_token = context.user_data.get("access_token", None)
    if not access_token:
        await update.message.reply_text("Avval tizimga kiring.")
        return

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(SCHEDULES_URL, headers=headers)

    if response.status_code == 200:
        schedules = response.json().get("results", [])
        if schedules:
            schedule_text = "\n\n".join(
                f"Guruh: {', '.join(group.get('name', 'Noma\'lum') for group in schedule.get('group', []))}\n"
                f"Fan: {schedule.get('subject', 'Noma\'lum')}\n"
                f"Boshlanish: {schedule.get('start_time', 'Noma\'lum')}\n"
                f"Tugash: {schedule.get('end_time', 'Noma\'lum')}\n"
                f"Xona: {schedule.get('room', 'Noma\'lum')}\n"
                f"Ustoz: {schedule.get('teacher', 'Noma\'lum')}"
                for schedule in schedules
            )
            await update.message.reply_text(f"Sizning dars jadvalingiz:\n\n{schedule_text}")
        else:
            await update.message.reply_text("Jadval topilmadi.")
    else:
        await update.message.reply_text("Jadvalni olishda xatolik yuz berdi.")


async def fetch_and_display_options(update, context: ContextTypes.DEFAULT_TYPE, endpoint, prompt, callback_prefix,
                                    page_url=None):
    query = update.callback_query
    await query.answer()

    url = page_url if page_url else f"{BASE_URL}/{endpoint}/"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        items = data.get("results", [])
        next_page = data.get("next", None)
        previous_page = data.get("previous", None)

        field_map = {"teachers": "username", "groups": "name", "rooms": "name", "subject": "name"}
        field = field_map.get(endpoint, "name")

        buttons = [
            InlineKeyboardButton(item.get(field, "Noma'lum"), callback_data=f"{callback_prefix}_{item['id']}")
            for item in items
        ]
        keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

        pagination_buttons = []
        if previous_page:
            context.user_data[f"{endpoint}_previous"] = previous_page
            pagination_buttons.append(
                InlineKeyboardButton("⬅ Oldingisi", callback_data=f"paginate_{endpoint}_previous"))
        if next_page:
            context.user_data[f"{endpoint}_next"] = next_page
            pagination_buttons.append(InlineKeyboardButton("Keyingisi ➡", callback_data=f"paginate_{endpoint}_next"))

        if pagination_buttons:
            keyboard.append(pagination_buttons)

        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="go_back")])

        await query.edit_message_text(prompt, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await query.edit_message_text("Ma'lumotlarni yuklashda xatolik yuz berdi.")


async def display_schedule(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    filter_type, filter_id = query.data.split("_")
    current_url = f"{BASE_URL}/schedules/?{filter_type}={filter_id}"
    response = requests.get(current_url)

    if response.status_code == 200:
        data = response.json()
        schedules = data.get("results", [])
        context.user_data[f"schedules_next"] = data.get("next", None)
        context.user_data[f"schedules_previous"] = data.get("previous", None)

        if schedules:
            schedule_text = "\n\n".join(
                f"Kun: {schedule.get('day_of_week', 'Noma\'lum')}\n"
                f"Boshlanish: {schedule.get('start_time', 'Noma\'lum')}\n"
                f"Tugash: {schedule.get('end_time', 'Noma\'lum')}\n"
                f"Guruh: {', '.join(group.get('name', 'Noma\'lum') for group in schedule.get('group', []))}\n"
                f"Fan: {schedule.get('subject', 'Noma\'lum')}\n"
                f"Xona: {schedule.get('room', 'Noma\'lum')}\n"
                f"Ustoz: {schedule.get('teacher', 'Noma\'lum')}\n"
                f"Xona raqami: {schedule.get('room_number', 'N/A')}\n"
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
            await query.edit_message_text("Bu filtrlash uchun jadval topilmadi.")
    else:
        await query.edit_message_text("Jadvalni olishda xatolik yuz berdi.")


async def get_groups(update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, context, "groups", "Guruhni tanlang:", "group")


async def get_teachers(update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, context, "teachers", "O'qituvchini tanlang:", "teacher")


async def get_rooms(update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, context, "rooms", "Xonani tanlang:", "room")


async def get_subject(update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, context, "subject", "Fanni tanlang:", "subject")


async def go_back(update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
