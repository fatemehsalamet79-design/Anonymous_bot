import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

ADMIN_ID = 6478179329
TOKEN = os.environ["BOT_TOKEN"]

# ارتباط پیام‌های دریافتی با فرستنده
users = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 🤍\n"
        "پیامت رو اینجا ناشناس بفرست؛ من دریافتش می‌کنم."
    )


async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # ذخیره شناسه فرستنده
    users[update.message.message_id] = user.id

    sent = await context.bot.send_message(
        chat_id=ADMIN_ID,
        text="📩 پیام ناشناس جدید:\n\n" + update.message.text
    )

    # شناسه پیام ادمین → شناسه فرستنده
    users[sent.message_id] = user.id


async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if not update.message.reply_to_message:
        return

    original_message_id = update.message.reply_to_message.message_id
    user_id = users.get(original_message_id)

    if user_id:
        await context.bot.send_message(
            chat_id=user_id,
            text="💌 پاسخ:\n\n" + update.message.text
        )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(
            filters.User(user_id=ADMIN_ID) & filters.REPLY,
            admin_reply
        )
    )

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_message
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
