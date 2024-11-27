from telegram.ext import ContextTypes

from bot2.config import BASE_URL
from bot2.handlers import fetch_and_display_options


async def search_handler(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["awaiting_search_query"] = query.data.split("_")[1]
    await query.edit_message_text("🔍 Qidiruv so'rovini kiriting:")




async def handle_search_query(update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_search_query" in context.user_data:
        endpoint = context.user_data.pop("awaiting_search_query")
        search_query = update.message.text
        context.user_data[f"{endpoint}_search"] = search_query
        await fetch_and_display_options(
            update=update,
            context=context,
            endpoint=endpoint,
            prompt=f"{endpoint.capitalize()} tanlang:",
            callback_prefix=f"view_{endpoint}"
        )


async def clear_search_handler(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Tugma ma'lumotidan endpointni ajratib olish
    callback_data = query.data
    if "clear_search_" in callback_data:
        endpoint = callback_data.replace("clear_search_", "")
    else:
        await query.edit_message_text("Xatolik yuz berdi. Tugma ma'lumotlari noto‘g‘ri.")
        return

    # Qidiruv holatini o'chirish
    context.user_data.pop(f"{endpoint}_search", None)

    # Dastlabki URL holatiga qaytish
    await fetch_and_display_options(
        update=update,
        context=context,
        endpoint=endpoint,
        prompt=f"{endpoint.capitalize()} tanlang:",
        callback_prefix=f"view_{endpoint}",
        page_url=f"{BASE_URL}/{endpoint}/"  # Bazaviy URL manzili
    )



