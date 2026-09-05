import os
import requests
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "").strip()

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")
    def log_message(self, format, *args): pass

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHandler).serve_forever(), daemon=True).start()

def generate_ai_response(user_message):
    system_prompt = "You are a 24-26 year old American female in NC/GA. Translate any non-English message mentally to English. Respond strictly in persona: Gen-Z, seductive, teasing, friendly, using slang. No quotes or meta comments."
    
    # Active models list for Groq
    models_to_try = [
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "llama-3.1-70b-versatile"
    ]
    
    groq_error = "API Key not found or invalid."
    
    if GROQ_API_KEY:
        for model in models_to_try:
            try:
                res = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": model,
                        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
                        "temperature": 0.7,
                        "max_tokens": 150
                    },
                    timeout=8
                )
                if res.status_code == 200:
                    return res.json()["choices"][0]["message"]["content"].strip()
                else:
                    groq_error = res.text
            except Exception as e:
                groq_error = str(e)

    # Fallback to free backup API if needed
    try:
        encoded_prompt = urllib.parse.quote(f"{system_prompt}\nUser says: {user_message}\nResponse:")
        res_fall = requests.get(f"https://text.pollinations.ai/{encoded_prompt}?model=openai", timeout=15)
        if res_fall.status_code == 200 and res_fall.text:
            return res_fall.text.strip()
    except Exception:
        pass

    return f"⚠️ Error Detail: {groq_error}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_ai_response(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
