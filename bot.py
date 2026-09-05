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

# Ultra-fast serverless Hugging Face Inference Endpoint
API_URL = "https://api-inference.huggingface.co/models/google/gemma-2-2b-it"
headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"} if HUGGINGFACE_TOKEN else {}

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

    prompt = f"""<start_of_turn>user
You are a 24-26-year-old American female living in North Carolina/Georgia. Respond in natural Gen-Z slang, casual phrasing, with a seductive, teasing, and polite tone for hookup/meetup coordination.

Instructions:
1. Translate any incoming user message (e.g. Bengali) into English mentally first.
2. Respond strictly in character (Gen-Z American female, seductive, friendly, using slang like 'fr', 'bestie', 'pull up', etc.).
3. Output ONLY the response text.

User message: {user_message}<end_of_turn>
<start_of_turn>model
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 100,
            "temperature": 0.7,
            "return_full_text": False
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=12)
        
        if response.status_code == 200:
            res_json = response.json()
            if isinstance(res_json, list) and len(res_json) > 0:
                bot_reply = res_json[0].get("generated_text", "").strip()
            else:
                bot_reply = "Hey bestie, pull up! What's the plan?"
        else:
            logger.warning(f"API non-200 status: {response.status_code}, fallback activated")
            bot_reply = "Hey! Just saw your message, what's on your mind?"

    except Exception as e:
        logger.error(f"API Request Exception: {e}")
        bot_reply = "Yo, pull up! Tell me what you're up to tonight."

    await update.message.reply_text(bot_reply)

# Main Execution Block
if not TELEGRAM_TOKEN:
    logger.error("ERROR: TELEGRAM_BOT_TOKEN is missing!")
else:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)
