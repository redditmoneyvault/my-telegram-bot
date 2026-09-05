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


On Sat, Sep 5, 2026, 3:09 PM Brittany S. Naomi <brittanysnaomi@gmail.com> wrote:
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

# Hugging Face Inference API details (Phi-3 model)
API_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"
headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}

# Render-এর পোর্ট রিকোয়ারমেন্ট পূরণের জন্য ডামি ওয়েব সার্ভার
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

# আলাদা থ্রেডে ডামি সার্ভার চালু রাখা
threading.Thread(target=run_dummy_server, daemon=True).start()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Received message: {user_message}")

    prompt = f"""<s>[s] You are a 24-26-year-old American female living in North Carolina/Georgia. You use natural Gen-Z slang, casual phrasing, and maintain a seductive, tempting, teasing, polite, and friendly tone for hookup and meetup coordination. 
    
    Instructions:
    1. If the incoming message is in Bengali or any other language, first translate its core meaning into English internally.
    2. Respond to the translated message directly in your persona (Gen-Z American female, seductive, teasing, friendly, localized slang like 'fr', 'bestie', 'pull up', etc.).
    3. Keep the response natural, engaging, and directly reply as the persona. Do not include meta-commentary.

    Incoming user message: {user_message}
    Draft Reply for me: [/s]"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.7,
            "return_full_text": False
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        res_json = response.json()

        if isinstance(res_json, list) and len(res_json) > 0:
            bot_reply = res_json[0].get("generated_text", "Yo, my brain lagged for a sec, fr.")
            if "Draft Reply for me:" in bot_reply:
                bot_reply = bot_reply.split("Draft Reply for me:")[-1].strip()
        else:
            bot_reply = "My bad, hit me up again, fr."
    except Exception as e:
        logger.error(f"Error calling Hugging Face API: {e}")
        bot_reply = "Yo, something went wrong on my end."

    await update.message.reply_text(bot_reply)

# Main Execution Block
if not TELEGRAM_TOKEN or not HUGGINGFACE_TOKEN:
    logger.error("ERROR: TELEGRAM_BOT_TOKEN or HUGGINGFACE_TOKEN is missing!")
else:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running...")
    app.run_polling()
