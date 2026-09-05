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

def generate_ai_response(user_message):
    prompt = f"""You are a 24-26-year-old American female living in North Carolina/Georgia. You use natural Gen-Z slang (like 'fr', 'bestie', 'pull up', 'no cap'), casual phrasing, and maintain a seductive, tempting, teasing, polite, and friendly tone for hookup and meetup coordination.

Instructions:
1. Translate any incoming message (such as Bengali or other languages) into English mentally first.
2. Respond to the translated message directly in your persona (Gen-Z American female, seductive, teasing, friendly).
3. Do not include meta comments, explanations, or quotes. Output ONLY the raw chat response.

User message: {user_message}"""

    # Method 1: Hugging Face Router API (Updated URL)
    if HUGGINGFACE_TOKEN:
        try:
            hf_url = "https://router.huggingface.co/hf-inference/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {HUGGINGFACE_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "meta-llama/Llama-3.2-3B-Instruct",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 120,
                "temperature": 0.7
            }
            res = requests.post(hf_url, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                data = res.json()
                reply = data["choices"][0]["message"]["content"].strip()
                if reply:
                    return reply
        except Exception as e:
            logger.error(f"Hugging Face Router error: {e}")

    # Method 2: High-speed Fallback (Pollinations AI Engine)
    try:
        pollination_url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": "You are a 24-26 y/o Gen-Z American girl from NC/GA, flirtatious, seductive, teasing, polite for meetup coordination. Translate input to English if needed and reply in character."},
                {"role": "user", "content": user_message}
            ],
            "model": "openai"
        }
        res = requests.post(pollination_url, json=payload, timeout=10)
        if res.status_code == 200 and res.text.strip():
            return res.text.strip()
    except Exception as e:
        logger.error(f"Pollinations Fallback error: {e}")

    return "Yo, my bad, was grabbing a drink! What were you saying, bestie?"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Received message: {user_message}")

    # Get AI generated response
    bot_reply = generate_ai_response(user_message)

    await update.message.reply_text(bot_reply)

# Main Execution Block
if not TELEGRAM_TOKEN:
    logger.error("ERROR: TELEGRAM_BOT_TOKEN is missing!")
else:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)
