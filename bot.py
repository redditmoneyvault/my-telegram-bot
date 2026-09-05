import os
import logging
import requests
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("TelegramBot")

# Load Telegram Token
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Render dummy HTTP server to bind port
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Telegram Bot is active and running!")
    def log_message(self, format, *args):
        pass

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

def get_dynamic_ai_response(user_message):
    system_prompt = (
        "You are a 24-26 year old American female living in NC/GA. "
        "Translate any non-English message (like Bengali) to English internally. "
        "Respond strictly in persona: Gen-Z, seductive, teasing, friendly, using slang like 'fr', 'bestie', 'pull up'. "
        "Do not output meta commentary or quotes."
    )
    
    full_prompt = f"{system_prompt}\nUser says: {user_message}\nResponse:"
    encoded_prompt = urllib.parse.quote(full_prompt)
    
    # Ultra-reliable direct API stream
    url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai"
    
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200 and res.text.strip():
            return res.text.strip()
    except Exception as e:
        logger.error(f"Pollinations GET Error: {e}")
        
    return "Yo, my brain lagged for a second, fr. Say that again?"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Received message: {user_message}")

    bot_reply = get_dynamic_ai_response(user_message)
    await update.message.reply_text(bot_reply)

# Main Execution Block
if not TELEGRAM_TOKEN:
    logger.error("ERROR: TELEGRAM_BOT_TOKEN is missing!")
else:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)
