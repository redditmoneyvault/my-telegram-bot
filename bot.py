import os
import logging
import requests
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

# Load tokens from environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
HUGGINGFACE_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")

# Reliable Hugging Face Model for fast responses
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Received message: {user_message}")

    prompt = f"""<s>[INST] You are a 24-26-year-old American female living in North Carolina/Georgia. You use natural Gen-Z slang, casual phrasing, and maintain a seductive, tempting, teasing, polite, and friendly tone for hookup and meetup coordination.

Instructions:
1. Translate any incoming message (like Bengali) into English mentally first.
2. Respond to the user's intent in your persona (Gen-Z American female, seductive, friendly, using slang like 'fr', 'bestie', 'pull up', etc.).
3. Give ONLY the direct reply in character. No meta comments.

User message: {user_message} [/INST]"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 120,
            "temperature": 0.7,
            "return_full_text": False
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=20)
        res_json = response.json()

        if isinstance(res_json, list) and len(res_json) > 0:
            bot_reply = res_json[0].get("generated_text", "").strip()
            if not bot_reply:
                bot_reply = "Yo, pull up! What's the plan?"
        elif isinstance(res_json, dict) and "error" in res_json:
            logger.error(f"Hugging Face Error: {res_json['error']}")
            bot_reply = "My model is waking up, send that again in 10 secs!"
        else:
            bot_reply = "Yo, my brain lagged for a sec. Say that again?"
    except Exception as e:
        logger.error(f"API Request Exception: {e}")
        bot_reply = "Yo, network acting up on my end, hit me up again!"

    await update.message.reply_text(bot_reply)

# Main Execution Block
if not TELEGRAM_TOKEN or not HUGGINGFACE_TOKEN:
    logger.error("ERROR: TELEGRAM_BOT_TOKEN or HUGGINGFACE_TOKEN is missing!")
else:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running...")
    app.run_polling()
