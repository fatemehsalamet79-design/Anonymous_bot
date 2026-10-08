import os
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# لاگ برای اینکه خطاها در Railway دیده شوند
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# آیدی عددی خودت
ADMIN_ID = 6478179329

# توکن از Railway گرفته می‌شود
TOKEN = os.environ["BOT_TOKEN"]

# ارتباط بین پیام دریافتی و فرستنده ناشناس
message_map = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 🤍\n\n"
        "پیامت رو ناشناس بفرست."
    )


# دریافت پیام از شخص ناشناس
async def anonymous_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message or not update.message.text:
        return

    sender_id = update.effective_chat.id
    text = update.message.text

    logger.info("Anonymous message received from %s", sender_id)

    # ارسال پیام برای تو
    sent_message = await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "📩 پیام ناشناس\n\n"
            f"{text}\n\n"
            "↩️ برای پاسخ، روی همین پیام Reply کن."
        )
    )

    # ذخیره اینکه این پیام متعلق به چه کسی است
    message_map[sent_message.message_id] = sender_id

    # به فرستنده می‌گوییم پیامش دریافت شده
    await update.message.reply_text(
        "پیامت با موفقیت ارسال شد 🤍"
    )


# پاسخ تو به پیام ناشناس
async def admin_reply(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    # فقط خودت اجازه پاسخ دادن داری
    if update.effective_user.id != ADMIN_ID:
        return

    if not update.message or not update.message.reply_to_message:
        return

    replied_message = update.message.reply_to_message

    # پیدا کردن صاحب پیام
    sender_id = message_map.get(replied_message.message_id)

    if not sender_id:
        await update.message.reply_text(
            "❌ این پیام دیگه قابل پاسخ دادن نیست."
        )
        return

    # فرستادن جواب برای همان شخص
    await context.bot.send_message(
        chat_id=sender_id,
        text=f"💌 پاسخ:\n\n{update.message.text}"
    )

    await update.message.reply_text(
        "✅ پاسخت برای فرستنده ارسال شد."
    )

    logger.info(
        "Reply sent to anonymous user %s",
        sender_id
    )


# نمایش خطاها در Railway
async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):
    logger.error(
        "Exception while handling update:",
        exc_info=context.error
    )


def main():
    app = Application.builder().token(TOKEN).build()

    # /start
    app.add_handler(
        CommandHandler("start", start)
    )

    # پاسخ دادن به پیام ناشناس
    app.add_handler(
        MessageHandler(
            filters.User(user_id=ADMIN_ID)
            & filters.REPLY
            & filters.TEXT,
            admin_reply
        )
    )

    # دریافت پیام‌های معمولی
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            anonymous_message
        )
    )

    # خطاها
    app.add_error_handler(error_handler)

    logger.info("Bot is starting...")

    app.run_polling()


if __name__ == "__main__":
    main()
