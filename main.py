import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ContextTypes, ChatJoinRequestHandler, CommandHandler
from dotenv import load_dotenv

# हमारे बनाए हुए मॉड्यूल्स को इम्पोर्ट करें
from config import ADMIN_IDS, MAIN_CHANNEL_LINK

load_dotenv()
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# --- फैंसी टेक्स्ट ---
START_MESSAGE = "Hᴇʟʟᴏ! I'ᴍ Aʟɪɴᴀ, ʏᴏᴜʀ ᴀᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴀʟ ᴀssɪsᴛᴀɴᴛ. I'ᴍ ᴡᴏʀᴋɪɴɢ ᴘᴇʀғᴇᴄᴛʟʏ!"
MAIN_CHANNEL_PROMPT = "Tᴏ ɢᴇᴛ ᴀᴄᴄᴇss, ᴘʟᴇᴀsᴇ ᴊᴏɪɴ ᴏᴜʀ ᴍᴀɪɴ ɴᴇᴛᴡᴏʀᴋ."

# --- Keep-Alive सर्वर ---
app = Flask('')
@app.route('/')
def home():
    return "Alina Bot is alive and running!"
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
def keep_alive():
    Thread(target=run_flask).start()

# --- हैंडलर्स ---
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start कमांड को हैंडल करता है।"""
    keyboard = [[InlineKeyboardButton("🚀 Jᴏɪɴ Mᴀɪɴ Cʜᴀɴɴᴇʟ 🚀", url=MAIN_CHANNEL_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(MAIN_CHANNEL_PROMPT, reply_markup=reply_markup)

async def new_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """नई ज्वाइन रिक्वेस्ट को ऑटो-अप्रूव करता है।"""
    try:
        await update.chat_join_request.approve()
        logger.info(f"Aᴘᴘʀᴏᴠᴇᴅ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ ғʀᴏᴍ {update.chat_join_request.from_user.id} ғᴏʀ ᴄʜᴀᴛ {update.chat_join_request.chat.id}")
    except Exception as e:
        logger.error(f"Fᴀɪʟᴇᴅ ᴛᴏ ᴀᴘᴘʀᴏᴠᴇ ᴊᴏɪɴ ʀᴇǫᴜᴇsᴛ: {e}")
        if ADMIN_IDS:
            try:
                await context.bot.send_message(chat_id=ADMIN_IDS[0], text=f"⚠️ Eʀʀᴏʀ ᴀᴘᴘʀᴏᴠɪɴɢ ʀᴇǫᴜᴇsᴛ: {e}")
            except Exception as admin_e:
                logger.error(f"Fᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ᴇʀʀᴏʀ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴ ᴛᴏ ᴀᴅᴍɪɴ: {admin_e}")

async def status_check_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """एडमिन को बॉट के चलने की पुष्टि देता है।"""
    if update.effective_user.id in ADMIN_IDS:
        await update.message.reply_text(START_MESSAGE)

# --- मुख्य फंक्शन ---
def main():
    if not TOKEN:
        logger.critical("TELEGRAM_BOT_TOKEN ɴᴏᴛ sᴇᴛ! Bᴏᴛ ᴄᴀɴɴᴏᴛ sᴛᴀʀᴛ.")
        return

    application = Application.builder().token(TOKEN).build()
    
    # हैंडलर्स को रजिस्टर करें
    application.add_handler(ChatJoinRequestHandler(new_join_request))
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("status", status_check_handler)) # एडमिन के लिए एक स्टेटस कमांड
    
    keep_alive()
    logger.info("Aʟɪɴᴀ Bᴏᴛ ɪs ʀᴇᴀᴅʏ ᴀɴᴅ ᴘᴏʟʟɪɴɢ!")
    application.run_polling()

if __name__ == '__main__':
    main()