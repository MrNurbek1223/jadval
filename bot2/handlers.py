import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import requests
from config import BASE_URL, SCHEDULES_URL, LOGIN_URL


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Davomat", callback_data="attendance"),
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

    access_token = context.user_data.get("access_token")

    if not access_token:
        await query.edit_message_text("Iltimos, email va parolingizni kiriting:\nFormat: email password")
        context.user_data["waiting_for_login"] = True
        return

    keyboard = [
        [InlineKeyboardButton("Davomat qilish", callback_data="do_attendance"),
         InlineKeyboardButton("Davomat ko'rish", callback_data="view_attendance")],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="go_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Davomat uchun quyidagi opsiyalardan birini tanlang:", reply_markup=reply_markup)


async def do_attendance(update, context: ContextTypes.DEFAULT_TYPE):
    access_token = context.user_data.get("access_token", None)
    if not access_token:
        if update.callback_query:
            await update.callback_query.edit_message_text("Avval tizimga kiring.")
        elif update.message:
            await update.message.reply_text("Avval tizimga kiring.")
        return

    page_url = context.user_data.get("current_schedule_page", SCHEDULES_URL)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(page_url, headers=headers)

    if response.status_code == 401:
        if update.callback_query:
            await update.callback_query.edit_message_text("Token eskirgan. Iltimos, qayta login qiling.")
        elif update.message:
            await update.message.reply_text("Token eskirgan. Iltimos, qayta login qiling.")
        context.user_data.pop("access_token", None)
        context.user_data.pop("email", None)
        context.user_data["waiting_for_login"] = True
        return

    if response.status_code == 200:
        data = response.json()
        schedules = data.get("results", [])
        next_page = data.get("next", None)
        previous_page = data.get("previous", None)

        schedule_text = "\n\n".join(
            f"{idx + 1}. 📅 Kun: {schedule.get('day_of_week', 'Noma\'lum')}\n"
            f"    🕒 Vaqt: {schedule.get('start_time', 'Noma\'lum')} - {schedule.get('end_time', 'Noma\'lum')}\n"
            f"    🎓 Fan: {schedule.get('subject', 'Noma\'lum')}\n"
            f"    🏫 Xona: {schedule.get('room', 'Noma\'lum')} ({schedule.get('room_number', 'N/A')})\n"
            f"    👥 Guruh: {', '.join(group.get('name', 'Noma\'lum') for group in schedule.get('group', []))}"
            for idx, schedule in enumerate(schedules)
        )

        schedule_buttons = [
            InlineKeyboardButton(f"{idx + 1}", callback_data=f"schedule_{schedule['id']}")
            for idx, schedule in enumerate(schedules)
        ]
        formatted_buttons = [schedule_buttons[i:i + 4] for i in range(0, len(schedule_buttons), 4)]

        pagination_buttons = []
        if previous_page:
            pagination_buttons.append(InlineKeyboardButton("⬅ Oldingisi", callback_data="attendance_previous"))
            context.user_data["attendance_previous_page"] = previous_page
        pagination_buttons.append(InlineKeyboardButton("❌ Orqaga", callback_data="attendance"))
        if next_page:
            pagination_buttons.append(InlineKeyboardButton("Keyingisi ➡", callback_data="attendance_next"))
            context.user_data["attendance_next_page"] = next_page

        formatted_buttons.append(pagination_buttons)

        reply_markup = InlineKeyboardMarkup(formatted_buttons)
        if update.callback_query:
            await update.callback_query.edit_message_text(
                f"Dars jadvallari:\n\n{schedule_text}", reply_markup=reply_markup
            )
        elif update.message:
            await update.message.reply_text(f"Dars jadvallari:\n\n{schedule_text}", reply_markup=reply_markup)
    else:
        if update.callback_query:
            await update.callback_query.edit_message_text("Jadvalni olishda xatolik yuz berdi.")
        elif update.message:
            await update.message.reply_text("Jadvalni olishda xatolik yuz berdi.")


async def unified_text_handler(update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("waiting_for_login"):
        user_input = update.message.text.split()
        if len(user_input) != 2:
            await update.message.reply_text(
                "Noto‘g‘ri format. Iltimos, email va parolni qaytadan kiriting.\nFormat: email password")
            return

        email, password = user_input

        try:

            response = requests.post(LOGIN_URL, json={"email": email, "password": password})
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access")
                refresh_token = token_data.get("refresh")
                role = token_data.get("role")

                if access_token and role:
                    # Token va foydalanuvchi ma'lumotlarini saqlash
                    context.user_data["access_token"] = access_token
                    context.user_data["refresh_token"] = refresh_token
                    context.user_data["role"] = role
                    context.user_data["waiting_for_login"] = False

                    # Roli asosida tugmalarni ko'rsatish
                    if role == "teacher":
                        keyboard = [
                            [InlineKeyboardButton("Davomat qilish", callback_data="do_attendance"),
                             InlineKeyboardButton("Davomat ko'rish", callback_data="view_attendance")],
                            [InlineKeyboardButton("🔙 Orqaga", callback_data="go_back")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(
                            "Xush kelibsiz, o'qituvchi! Quyidagi opsiyalardan birini tanlang:",
                            reply_markup=reply_markup
                        )
                    elif role == "student":
                        keyboard = [
                            [InlineKeyboardButton("Davomat ko'rish", callback_data="view_attendance")],
                            [InlineKeyboardButton("🔙 Orqaga", callback_data="go_back")]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await update.message.reply_text(
                            "Xush kelibsiz, talaba! Quyidagi opsiyani tanlang:",
                            reply_markup=reply_markup
                        )
                    else:
                        await update.message.reply_text("Roli aniqlanmadi. Iltimos, administrator bilan bog'laning.")
                else:
                    await update.message.reply_text("Login amalga oshmadi. Token yoki rol olinmadi.")
            else:
                await update.message.reply_text(
                    "Login amalga oshirishda xatolik yuz berdi. Email va parolni qayta tekshirib ko'ring.")
        except requests.RequestException as e:
            await update.message.reply_text(f"Tizimga ulanishda xatolik yuz berdi: {e}")
        return

    if context.user_data.get("awaiting_search_query"):
        endpoint = context.user_data.pop("awaiting_search_query")
        search_query = update.message.text.strip()
        if not search_query:
            await update.message.reply_text("Qidiruv so‘rovi bo‘sh bo‘lmasligi kerak. Qaytadan urinib ko‘ring.")
            return

        context.user_data[f"{endpoint}_search"] = search_query
        await fetch_and_display_options(
            update=update,
            context=context,
            endpoint=endpoint,
            prompt=f"{endpoint.capitalize()} tanlang:",
            callback_prefix=f"view_{endpoint}"
        )
        return

    await update.message.reply_text("Noma'lum so'rov. Iltimos, tegishli tugmani tanlang yoki yordam so'rang.")


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
                headers = {"Authorization": f"Bearer {access_token}"}
                user_info_response = requests.get(f"{BASE_URL}/user-info/", headers=headers)
                if user_info_response.status_code == 200:
                    user_data = user_info_response.json()
                    context.user_data["access_token"] = access_token
                    context.user_data["role"] = user_data.get("role", "unknown")
                    context.user_data["waiting_for_login"] = False

                    await update.message.reply_text("Login muvaffaqiyatli amalga oshirildi.")
                    await attendance_handler(update, context)
                else:
                    await update.message.reply_text("Foydalanuvchi ma'lumotlarini olishda xatolik yuz berdi.")
            else:
                await update.message.reply_text("Login amalga oshirilmadi. Iltimos, qayta urinib ko‘ring.")
        else:
            await update.message.reply_text("Login xatolik yuz berdi. Iltimos, qayta urinib ko‘ring.")
        context.user_data["waiting_for_login"] = False


async def get_teacher_schedule(update, context):
    access_token = context.user_data.get("access_token", None)
    if not access_token:
        if update.callback_query:
            await update.callback_query.edit_message_text("Avval tizimga kiring.")
        elif update.message:
            await update.message.reply_text("Avval tizimga kiring.")
        return

    page_url = context.user_data.get("current_schedule_page", SCHEDULES_URL)
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(page_url, headers=headers)

    if response.status_code == 401:
        if update.callback_query:
            await update.callback_query.edit_message_text("Token eskirgan. Iltimos, qayta login qiling.")
        elif update.message:
            await update.message.reply_text("Token eskirgan. Iltimos, qayta login qiling.")
        context.user_data.pop("access_token", None)
        context.user_data.pop("email", None)
        context.user_data["waiting_for_login"] = True
        return

    if response.status_code == 200:
        data = response.json()
        schedules = data.get("results", [])
        next_page = data.get("next", None)
        previous_page = data.get("previous", None)

        schedule_text = "\n\n".join(
            f"{idx + 1}. 📅 Kun: {schedule.get('day_of_week', 'Noma\'lum')}\n"
            f"    🕒 Vaqt: {schedule.get('start_time', 'Noma\'lum')} - {schedule.get('end_time', 'Noma\'lum')}\n"
            f"    🎓 Fan: {schedule.get('subject', 'Noma\'lum')}\n"
            f"    🏫 Xona: {schedule.get('room', 'Noma\'lum')} ({schedule.get('room_number', 'N/A')})\n"
            f"    👥 Guruh: {', '.join(group.get('name', 'Noma\'lum') for group in schedule.get('group', []))}"
            for idx, schedule in enumerate(schedules)
        )

        schedule_buttons = [
            InlineKeyboardButton(f"{idx + 1}", callback_data=f"schedule_{schedule['id']}")
            for idx, schedule in enumerate(schedules)
        ]
        formatted_buttons = [schedule_buttons[i:i + 4] for i in range(0, len(schedule_buttons), 4)]

        pagination_buttons = []
        if previous_page:
            pagination_buttons.append(InlineKeyboardButton("⬅ Oldingisi", callback_data="attendance_previous"))
            context.user_data["attendance_previous_page"] = previous_page
        pagination_buttons.append(InlineKeyboardButton("❌ Orqaga", callback_data="go_back"))
        if next_page:
            pagination_buttons.append(InlineKeyboardButton("Keyingisi ➡", callback_data="attendance_next"))
            context.user_data["attendance_next_page"] = next_page

        formatted_buttons.append(pagination_buttons)

        reply_markup = InlineKeyboardMarkup(formatted_buttons)
        if update.callback_query:
            await update.callback_query.edit_message_text(
                f"Dars jadvallari:\n\n{schedule_text}", reply_markup=reply_markup
            )
        elif update.message:
            await update.message.reply_text(f"Dars jadvallari:\n\n{schedule_text}", reply_markup=reply_markup)
    else:
        if update.callback_query:
            await update.callback_query.edit_message_text("Jadvalni olishda xatolik yuz berdi.")
        elif update.message:
            await update.message.reply_text("Jadvalni olishda xatolik yuz berdi.")


async def fetch_and_display_options(
        update, context: ContextTypes.DEFAULT_TYPE, endpoint, prompt, callback_prefix, page_url=None
):
    """
    Foydalanuvchiga tanlash uchun opsiyalarni ko'rsatadi va API orqali natijalarni olib keladi.
    """
    query = update.callback_query if update.callback_query else None
    message = update.message if update.message else None

    if query:
        await query.answer()

    base_url = f"{BASE_URL}/{endpoint}/"
    url = page_url or context.user_data.get(f"{endpoint}_current", base_url)
    search_query = context.user_data.get(f"{endpoint}_search", None)

    if search_query and 'search=' not in url:
        url += f"&search={search_query}" if "?" in url else f"?search={search_query}"

    try:

        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        error_message = f"Ma'lumotlarni yuklashda xatolik yuz berdi: {e}"

        if query:
            await query.edit_message_text(error_message)
        elif message:
            await message.reply_text(error_message)
        return

    data = response.json()

    items = data.get("results", [])
    next_page = data.get("next", None)
    previous_page = data.get("previous", None)

    context.user_data[f"{endpoint}_current"] = url
    context.user_data[f"{endpoint}_next"] = next_page
    context.user_data[f"{endpoint}_previous"] = previous_page

    field_map = {"teachers": "username", "groups": "name", "rooms": "name", "subject": "name"}
    field = field_map.get(endpoint, "name")

    buttons = [
        InlineKeyboardButton(
            item.get(field, "Noma'lum"),
            callback_data=f"{callback_prefix}_{item['id']}"
        )
        for item in items
    ]

    keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

    pagination_buttons = []
    if previous_page:
        pagination_buttons.append(
            InlineKeyboardButton("⬅ Oldingisi", callback_data=f"paginate_{endpoint}_previous")
        )
    if next_page:
        pagination_buttons.append(
            InlineKeyboardButton("Keyingisi ➡", callback_data=f"paginate_{endpoint}_next")
        )
    if pagination_buttons:
        keyboard.append(pagination_buttons)

    search_buttons = [InlineKeyboardButton("🔍 Qidiruv", callback_data=f"search_{endpoint}")]
    if search_query:
        search_buttons.append(InlineKeyboardButton("❌ Qidiruvni tozalash", callback_data=f"clear_search_{endpoint}"))
    keyboard.append(search_buttons)

    keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="view_schedule")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    if query:
        await query.edit_message_text(text=prompt, reply_markup=reply_markup)
    elif message:
        await message.reply_text(text=prompt, reply_markup=reply_markup)


async def paginate(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        _, endpoint, direction = query.data.split("_")
    except ValueError:
        await query.edit_message_text("Xatolik yuz berdi. Tugma ma'lumotlari noto‘g‘ri.")
        return

    current_url = context.user_data.get(f"{endpoint}_{direction}")
    if not current_url:
        await query.edit_message_text("Sahifa ma'lumotlari mavjud emas.")
        return

    await fetch_and_display_options(
        update=update,
        context=context,
        endpoint=endpoint,
        prompt=f"{endpoint.capitalize()} tanlang:",
        callback_prefix=f"view_{endpoint}",
        page_url=current_url
    )


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
                f"📅 Kun: {schedule.get('day_of_week', 'Noma\'lum')}\n"
                f"⏰ Boshlanish: {schedule.get('start_time', 'Noma\'lum')} | "
                f"Tugash: {schedule.get('end_time', 'Noma\'lum')}\n"
                f"👥 Guruh: {', '.join(group.get('name', 'Noma\'lum') for group in schedule.get('group', []))}\n"
                f"📚 Fan: {schedule.get('subject', 'Noma\'lum')}\n"
                f"🏫 Xona: {schedule.get('room', 'Noma\'lum')} | "
                f"Raqam: {schedule.get('room_number', 'N/A')}\n"
                f"👨‍🏫 Ustoz: {schedule.get('teacher', 'Noma\'lum')}\n"
                f"🔢 Sessiya: {schedule.get('session_number', 'Noma\'lum')}"
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
            keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="view_schedule")])

            await query.edit_message_text(f"Jadval:\n\n{schedule_text}", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text("Bu filtrlash uchun jadval topilmadi.")
    else:
        await query.edit_message_text("Jadvalni olishda xatolik yuz berdi.")


#####################################


async def get_schedule_groups(update, context):
    query = update.callback_query
    schedule_id = query.data.split("_")[1]
    context.user_data["schedule_id"] = schedule_id

    response = requests.get(f"http://127.0.0.1:8000/schedule/{schedule_id}/groups/")
    if response.status_code == 200:
        groups = response.json()
        if not groups:
            await query.edit_message_text("Bu dars jadvaliga tegishli guruhlar mavjud emas.")
            return

        keyboard = [
            [InlineKeyboardButton(
                f"Guruh: {group['name']} | Talabalar soni: {len(group.get('students', []))}",
                callback_data=f"attendance_group_{group['id']}"
            )]
            for group in groups
        ]
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="do_attendance")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Quyidagi guruhlardan birini tanlang:", reply_markup=reply_markup)
    else:
        await query.edit_message_text("Guruhlarni yuklashda xatolik yuz berdi.")


async def get_group_students(update, context):
    query = update.callback_query
    group_id = query.data.split("_")[2]
    context.user_data["group_id"] = group_id

    response = requests.get(f"{BASE_URL}/groups/{group_id}/students/")
    if response.status_code == 200:
        students = response.json()
        context.user_data["absent_students"] = []

        keyboard = []
        for student in students:
            student_buttons = [
                InlineKeyboardButton(f"{student['username']} - Sababli",
                                     callback_data=f"toggle_{student['id']}_reasoned"),
                InlineKeyboardButton(f"{student['username']} - Sababsiz",
                                     callback_data=f"toggle_{student['id']}_unreasoned"),
            ]
            keyboard.append(student_buttons)

        keyboard.append([InlineKeyboardButton("Davomatni tasdiqlash", callback_data="confirm_attendance")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text("Talabalar uchun sababni tanlang:", reply_markup=reply_markup)
    else:
        await query.edit_message_text("Talabalarni yuklashda xatolik yuz berdi.")


async def toggle_student(update, context):
    query = update.callback_query
    data = query.data.split("_")
    student_id = int(data[1])
    reason = data[2] if len(data) > 2 else None

    absent_students = context.user_data.get("absent_students", [])

    existing_student = next((s for s in absent_students if s["student_id"] == student_id), None)

    if existing_student:
        if reason:

            existing_student["reason"] = reason
        else:

            absent_students = [s for s in absent_students if s["student_id"] != student_id]
    else:

        absent_students.append({"student_id": student_id, "reason": reason or "unreasoned"})

    context.user_data["absent_students"] = absent_students

    await query.answer(
        f"Talaba {'sababli' if reason == 'reasoned' else 'sababsiz' if reason == 'unreasoned' else 'belgilandi'}.")


async def confirm_attendance(update, context):
    query = update.callback_query

    access_token = context.user_data.get("access_token")
    if not access_token:
        await query.edit_message_text("Xatolik: tizimga login qilinmagan.")
        return

    schedule_id = context.user_data.get("schedule_id")
    group_id = context.user_data.get("group_id")
    absent_students = context.user_data.get("absent_students", [])

    for student in absent_students:
        if "reason" not in student:
            student["reason"] = "unreasoned"

    payload = {
        "schedule": schedule_id,
        "group": group_id,
        "absent_students": absent_students,
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(f"{BASE_URL}/attendance/", json=payload, headers=headers)

    if response.status_code == 201:
        await query.edit_message_text("Davomat muvaffaqiyatli saqlandi!")
    else:
        error_message = response.json().get("detail", "Xatolik yuz berdi.")
        await query.edit_message_text(f"Davomatni saqlashda xatolik yuz berdi: {error_message}")


async def view_attendance(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    access_token = context.user_data.get("access_token")
    role = context.user_data.get("role")

    if not access_token or not role:
        await query.edit_message_text("Xatolik: tizimga kirish ma'lumotlari mavjud emas.")
        return

    if role == "teacher":
        keyboard = [
            [InlineKeyboardButton("Guruhlar bo'yicha", callback_data="attendance_view_groups"),
             InlineKeyboardButton("Fanlar bo'yicha", callback_data="attendance_view_subjects")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="go_back")]
        ]
    elif role == "student":
        keyboard = [
            [InlineKeyboardButton("Fanlar bo'yicha", callback_data="attendance_view_subjects")],
            [InlineKeyboardButton("🔙 Orqaga", callback_data="go_back")]
        ]
    else:
        await query.edit_message_text("Roli aniqlanmadi. Administrator bilan bog'laning.")
        return

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Davomatni ko‘rish uchun quyidagi opsiyalardan birini tanlang:",
                                  reply_markup=reply_markup)


async def view_groups(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    access_token = context.user_data.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}


    current_page_url = context.user_data.get("groups_current_page", f"{BASE_URL}/groups/")
    response = requests.get(current_page_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        groups = data.get("results", []) if isinstance(data, dict) else []

        if not groups:
            await query.edit_message_text("❌ Guruhlar ro‘yxati mavjud emas.")
            return

        keyboard = [
            [InlineKeyboardButton(f"{group['name']}", callback_data=f"attendance_group1_{group['id']}")]
            for group in groups
        ]

        # Paginatsiya tugmalarini qo‘shish
        pagination_buttons = []
        if data.get("previous"):
            pagination_buttons.append(InlineKeyboardButton("⬅ Oldingi", callback_data="paginate1_groups_previous"))
            context.user_data["groups_previous_page"] = data["previous"]
        if data.get("next"):
            pagination_buttons.append(InlineKeyboardButton("Keyingi ➡", callback_data="paginate1_groups_next"))
            context.user_data["groups_next_page"] = data["next"]

        if pagination_buttons:
            keyboard.append(pagination_buttons)

        # Orqaga qaytish tugmasi
        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="view_attendance")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Guruhlar ro‘yxatidan birini tanlang:", reply_markup=reply_markup)
    else:
        await query.edit_message_text("❌ Guruh ma'lumotlarini olishda xatolik yuz berdi.")



async def view_subjects(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    access_token = context.user_data.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}


    current_page_url = context.user_data.get("subjects_current_page", f"{BASE_URL}/subject/")
    response = requests.get(current_page_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        subjects = data.get("results", []) if isinstance(data, dict) else []

        if not subjects:
            await query.edit_message_text("❌ Fanlar ro‘yxati mavjud emas.")
            return


        keyboard = [
            [InlineKeyboardButton(f"{subject['name']}", callback_data=f"attendance_subject_{subject['id']}")]
            for subject in subjects
        ]


        pagination_buttons = []
        if data.get("previous"):
            pagination_buttons.append(InlineKeyboardButton("⬅ Oldingi", callback_data="paginate2_subjects_previous"))
            context.user_data["subjects_previous_page"] = data["previous"]
        if data.get("next"):
            pagination_buttons.append(InlineKeyboardButton("Keyingi ➡", callback_data="paginate2_subjects_next"))
            context.user_data["subjects_next_page"] = data["next"]

        if pagination_buttons:
            keyboard.append(pagination_buttons)


        keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="view_attendance")])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Fanlardan birini tanlang:", reply_markup=reply_markup)
    else:
        await query.edit_message_text("❌ Fan ma'lumotlarini olishda xatolik yuz berdi.")


async def paginate_subjects(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()


    direction = query.data.split("_")[2]
    page_url = context.user_data.get(f"subjects_{direction}_page")

    if not page_url:
        await query.edit_message_text("❌ Paginatsiya uchun sahifa topilmadi.")
        return


    context.user_data["subjects_current_page"] = page_url
    await view_subjects(update, context)



async def format_attendance_data(attendance_data):
    formatted_text = ""
    for record in attendance_data:
        formatted_text += (
            f"📚 *Fan*: {record['Fan']}\n"
            f"📅 *Sana*: {record['Sana']}\n"
            f"👤 *Talaba*: {record['Talaba']}\n\n"
        )
    return formatted_text.strip()


async def view_group_attendance(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()


    group_id = query.data.split("_")[2]

    access_token = context.user_data.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    attendance_url = f"{BASE_URL}/attendance-statistics/?group_id={group_id}"
    response = requests.get(attendance_url, headers=headers)

    if response.status_code == 200:
        attendance_data = response.json()

        if not attendance_data:
            keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="attendance_view_groups")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ Ushbu guruh uchun dars qoldirgan talabalar mavjud emas.",
                reply_markup=reply_markup
            )
            return


        attendance_text = "\n\n".join([
            f"📚 Fan: {item['Fan']}\n📅 Sana: {item['Sana']}\n👤 Talaba: {item['Talaba']}"
            for item in attendance_data
        ])
        keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="attendance_view_groups")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"Guruh bo‘yicha davomat:\n\n{attendance_text}", reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="attendance_view_groups")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "❌ Davomat ma'lumotlarini olishda xatolik yuz berdi.",
            reply_markup=reply_markup
        )



async def paginate_groups(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    direction = query.data.split("_")[2]
    page_url = context.user_data.get(f"groups_{direction}_page")

    if not page_url:
        await query.edit_message_text("❌ Paginatsiya uchun sahifa topilmadi.")
        return

    context.user_data["groups_current_page"] = page_url
    await view_groups(update, context)


async def view_subject_attendance(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Callback dan subject_id ni olish
    subject_id = query.data.split("_")[2]

    # Access token va rolni olish
    access_token = context.user_data.get("access_token")
    role = context.user_data.get("role")  # Role: "teacher" yoki "student"
    headers = {"Authorization": f"Bearer {access_token}"}

    # API ga so‘rov yuborish
    attendance_url = f"{BASE_URL}/attendance-statistics/?subject_id={subject_id}"
    response = requests.get(attendance_url, headers=headers)

    if response.status_code == 200:
        attendance_data = response.json()

        if not attendance_data:
            keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="attendance_view_subjects")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "❌ Ushbu fan uchun davomat ma’lumotlari mavjud emas.",
                reply_markup=reply_markup
            )
            return

        # Rolega qarab davomat ma'lumotlarini formatlash
        if role == "teacher":
            attendance_text = "\n\n".join([
                f"📚 Fan: {item['Fan']}\n📅 Sana: {item['Sana']}\n👤 Talaba: {item['Talaba']}\n"
                for item in attendance_data
            ])
        elif role == "student":
            attendance_text = "\n".join([
                f"📚 Fan: {item['Fan']}\n📅 Sana: {item['Sana']}\n"
                for item in attendance_data
            ])
        else:
            await query.edit_message_text("❌ Noma'lum rol. Administrator bilan bog‘laning.")
            return

        # Tugmalarni qo‘shish
        keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="attendance_view_subjects")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"Davomat ma’lumotlari:\n\n{attendance_text}", reply_markup=reply_markup)
    else:
        keyboard = [[InlineKeyboardButton("🔙 Orqaga", callback_data="attendance_view_subjects")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "❌ Davomat ma'lumotlarini olishda xatolik yuz berdi.",
            reply_markup=reply_markup
        )



async def view_student_attendance(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    subject_id = query.data.split("_")[2]

    access_token = context.user_data.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}

    attendance_url = f"{BASE_URL}/attendance-statistics/?subject_id={subject_id}"
    response = requests.get(attendance_url, headers=headers)

    if response.status_code == 200:
        attendance_data = response.json()
        attendance_text = "\n".join([
            f"Sana: {item['date']} | Holat: {item['status']}"
            for item in attendance_data
        ])
        await query.edit_message_text(f"Sizning davomatingiz:\n\n{attendance_text}")
    else:
        await query.edit_message_text("Davomat ma'lumotlarini olishda xatolik yuz berdi.")


async def get_groups(update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, context, "groups", "Groups tanlang:", "group")


async def get_teachers(update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, context, "teachers", "Teachers tanlang:", "teacher")


async def get_rooms(update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, context, "rooms", "Rooms tanlang:", "room")


async def get_subject(update, context: ContextTypes.DEFAULT_TYPE):
    await fetch_and_display_options(update, context, "subject", "Subject tanlang:", "subject")


async def go_back(update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)
