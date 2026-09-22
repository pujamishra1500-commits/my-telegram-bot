import logging
import json
import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = "8897699239:AAFAVpZoPFyV5Nm4G7ZTOFNFQzGtSLvl8Tg"
MAIN_ADMIN = 8665286254
DATA_FILE = "bot_data.json"

user_states = {}

# 24/7 Keeping Alive Web Server
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is alive and running 24/7!")
    def log_message(self, format, *args):
        return

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), KeepAliveHandler)
    server.serve_forever()

def start_keep_alive():
    t = threading.Thread(target=run_web_server, daemon=True)
    t.start()

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict): return data
        except Exception as e:
            logging.error(f"Error reading JSON: {e}")
    return {
        "admins": [MAIN_ADMIN], "photo": None, "video": None, "voice": None, "voice_caption": None,
        "apk_file": None, "apk_caption": "🎉 <b>Congratulations!</b> Here is your APK file.",
        "start_text": "🎭 <b>Welcome {name}</b> 🎭\n\n📢 <b>Join All Channels To Unlock</b> 🎯\n\n🔥 <b>How To Get Key</b> 🔑",
        "get_key_text": "GET KEY🔐", "get_key_link": "https://t.me/example",
        "slots": [{"name": f"CHANNEL {i+1}", "link": "https://t.me/example"} for i in range(6)]
    }

def save_data(data):
    try:
        with open(f"{DATA_FILE}.tmp", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(f"{DATA_FILE}.tmp", DATA_FILE)
    except Exception as e:
        logging.error(f"Error saving data: {e}")

db = load_data()

def is_admin(user_id):
    return user_id in db.get("admins", [MAIN_ADMIN])

async def send_start_panel(user, send_func):
    try:
        raw_caption = db.get("start_text", "")
        caption = raw_caption.replace("{name}", user.first_name if user.first_name else "User")
        keyboard = []
        slots = db.get("slots", [])
        for i in range(0, len(slots), 2):
            row = [InlineKeyboardButton(slots[i]['name'], url=slots[i]['link'])]
            if i + 1 < len(slots):
                row.append(InlineKeyboardButton(slots[i+1]['name'], url=slots[i+1]['link']))
            keyboard.append(row)
        keyboard.append([
            InlineKeyboardButton(db.get("get_key_text", "GET KEY🔐"), url=db.get("get_key_link", "https://t.me/example")),
            InlineKeyboardButton("✅ CHECK JOINED 🚀", callback_data="check_joined")
        ])
        markup = InlineKeyboardMarkup(keyboard)

        if db.get("video"): await send_func.reply_video(video=db["video"], caption=caption, reply_markup=markup, parse_mode="HTML")
        elif db.get("photo"): await send_func.reply_photo(photo=db["photo"], caption=caption, reply_markup=markup, parse_mode="HTML")
        else: await send_func.reply_text(caption, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user and update.message:
        await send_start_panel(update.effective_user, update.message)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Error: {context.error}")

def main():
    start_keep_alive()
    app = Application.builder().token(BOT_TOKEN).connect_timeout(30.0).read_timeout(30.0).build()
    app.add_handler(CommandHandler("start", start))
    app.add_error_handler(error_handler)
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
                      
