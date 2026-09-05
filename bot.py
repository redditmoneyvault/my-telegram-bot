import os
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")
    def log_message(self, format, *args): pass

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHandler).serve_forever(), daemon=True).start()

def generate_ai_response(user_message):
    if not GROQ_API_KEY:
        return "⚠️ Render-এ GROQ_API_KEY সেট করা নেই! দয়া করে Environment Variables-এ গিয়ে সেটি অ্যাড করে Save করুন।"

    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": "llama3-8b-8192", 
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a 24-26 year old American female in NC/GA. Translate any non-English message mentally to English. Respond strictly in persona: Gen-Z, seductive, teasing, friendly, using slang. No quotes or meta comments."
                },
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        res = requests.post(
            url, 
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}, 
            json=payload, 
            timeout=10
        )
        
        if res.status_code == 200:
            return res.json()["choices"][0]["message"]["content"].strip()
        return f"⚠️ API Error: {res.text}"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_ai_response(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
