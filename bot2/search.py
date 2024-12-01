from telegram.ext import ContextTypes
from bot2.config import BASE_URL
from bot2.handlers import fetch_and_display_options

async def search_handler(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        endpoint = query.data.split("_")[1]
        context.user_data["awaiting_search_query"] = endpoint
        await query.answer()
        await query.edit_message_text("🔍 Qidiruv uchun matn kiriting:")
    except IndexError:
        await query.edit_message_text("Xato: Endpoint noto‘g‘ri yoki tugma ma'lumotlari buzilgan.")




async def handle_search_query(update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_search_query" in context.user_data:
        endpoint = context.user_data.pop("awaiting_search_query")
        search_query = update.message.text.strip()

        if not search_query:
            await update.message.reply_text("Qidiruv so‘rovi bo‘sh bo‘lmasligi kerak. Iltimos, qayta urinib ko‘ring.")
            return

        context.user_data[f"{endpoint}_search"] = search_query
        await fetch_and_display_options(
            update=update,
            context=context,
            endpoint=endpoint,
            prompt=f"{endpoint.capitalize()} natijalari:",
            callback_prefix=f"view_{endpoint}"
        )
    else:
        await update.message.reply_text("Xato: Qidiruv so'rovini kiritish jarayoni noto'g'ri boshqarilmoqda.")



async def clear_search_handler(update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()


    try:
        endpoint = query.data.split("_")[2]
        if not endpoint:
            raise ValueError("Endpoint qiymati topilmadi.")
    except (IndexError, ValueError) as e:
        await query.edit_message_text("Xato: Endpointni aniqlashda muammo.")
        return


    context.user_data.pop(f"{endpoint}_search", None)


    api_url = f"{BASE_URL}/{endpoint}/"

    try:
        await fetch_and_display_options(
            update=update,
            context=context,
            endpoint=endpoint,
            prompt=f"{endpoint.capitalize()} uchun barcha ro‘yxat:",
            callback_prefix=f"view_{endpoint}",
            page_url=api_url
        )
    except Exception as e:
        await query.edit_message_text(f"Ma'lumotlarni yuklashda xatolik yuz berdi: {str(e)}")










