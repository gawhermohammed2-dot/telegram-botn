import os
import uuid
import asyncio
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8394910472:AAEPTlxuTmju7uwhEm_Ymj72xBSQkKELNXA"

# رابط السيرفر (IP أو دومين)
WEBHOOK_URL = "https://YOUR_DOMAIN_OR_IP"

PORT = 8000
DOWNLOAD_FOLDER = "downloads"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

user_links = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 أرسل الرابط للتحميل")


def download(url, fmt):
    filename = str(uuid.uuid4())

    ydl_opts = {
        "format": fmt,
        "outtmpl": f"{DOWNLOAD_FOLDER}/{filename}.%(ext)s",
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)
        return ydl.prepare_filename(info)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    if not url.startswith("http"):
        return

    user_id = update.effective_chat.id
    user_links[user_id] = url

    keyboard = [
        [
            InlineKeyboardButton("🎬 فيديو", callback_data="video"),
            InlineKeyboardButton("🎵 صوت", callback_data="audio")
        ]
    ]

    await update.message.reply_text("اختر:", reply_markup=InlineKeyboardMarkup(keyboard))


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.message.chat.id
    url = user_links.get(user_id)

    await query.edit_message_text("⏳ جاري التحميل...")

    fmt = "bestaudio" if query.data == "audio" else "bestvideo+bestaudio/best"

    file_path = await asyncio.to_thread(download, url, fmt)

    with open(file_path, "rb") as f:
        if query.data == "audio":
            await context.bot.send_audio(user_id, f)
        else:
            await context.bot.send_video(user_id, f)

    os.remove(file_path)
    await query.message.delete()


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button))

    print("✅ Webhook Bot Running 24/7")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )


if __name__ == "__main__":
    main()