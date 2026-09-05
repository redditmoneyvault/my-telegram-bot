import os
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")
    def log_message(self, format, *args): pass

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHandler).serve_forever(), daemon=True).start()

def generate_ai_response(user_message):
    if not GEMINI_API_KEY:
        return "⚠️ Error: GEMINI_API_KEY is missing in Render Environment Variables!"

    system_prompt = "You are a 24-26 year old American female in NC/GA. Translate any non-English message mentally to English. Respond strictly in persona: Gen-Z, seductive, teasing, friendly, using slang. No quotes or meta comments."
    
    # Using Google's ultra-stable Gemini 1.5 Flash API directly via REST
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": f"{system_prompt}\nUser says: {user_message}"}]}
        ]
    }
    
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            return f"⚠️ API Error: {res.text}"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_ai_response(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
