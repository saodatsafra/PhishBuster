from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes


BOT_TOKEN = '7752412843:AAF0dZ0TWhJvjQtyIgg41FjyuY_4fDKNgg4'
WEBAPP_URL = 'https://phishbuster-pn5v.onrender.com/'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton(text="Open Web App", web_app=WebAppInfo(url=WEBAPP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome! Tap the button below to use the PhishBuster app inside Telegram.",
        reply_markup=reply_markup
    )

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
