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

# Environment Variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

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
    system_instruction = (
        "You are a 24-26 year old American female living in NC/GA. "
        "If the user writes in any other language (like Bengali), translate it mentally to English first. "
        "Respond strictly in persona: Gen-Z, seductive, teasing, friendly, using slang like 'fr', 'bestie', 'pull up'. "
        "Do not include quotes or meta comments. Output ONLY the response text."
    )

    # 1. Try Groq API directly via REST with valid model ID
    if GROQ_API_KEY:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            # Supported and verified Groq models
            for model_id in ["llama-3.1-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"]:
                payload = {
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 120
                }
                res = requests.post(url, headers=headers, json=payload, timeout=8)
                if res.status_code == 200:
                    data = res.json()
                    reply = data["choices"][0]["message"]["content"].strip()
                    if reply:
                        return reply
        except Exception as e:
            logger.error(f"Groq Direct API Error: {e}")

    # 2. Universal Ultra-Fast Fallback (Gemma Engine)
    try:
        fb_url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            "model": "mistral"
        }
        res = requests.post(fb_url, json=payload, timeout=8)
        if res.status_code == 200 and res.text.strip():
            return res.text.strip()
    except Exception as e:
        logger.error(f"Fallback Error: {e}")

    return "Hey babe! What was that? Say it one more time."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Received message: {user_message}")

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
