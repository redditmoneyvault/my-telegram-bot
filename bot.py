import os
import requests
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active!")
    def log_message(self, format, *args): pass

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 10000))), SimpleHandler).serve_forever(), daemon=True).start()

def generate_ai_response(user_message):
    system_prompt = "You are a 24-26 year old American female in NC/GA. Translate any non-English message mentally to English. Respond strictly in persona: Gen-Z, seductive, teasing, friendly, using slang. No quotes or meta comments."
    
    try:
        full_prompt = f"{system_prompt}\nUser: {user_message}\nReply:"
        encoded_prompt = urllib.parse.quote(full_prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai"
        
        res = requests.get(url, timeout=15)
        if res.status_code == 200 and res.text:
            return res.text.strip()
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
        
    return "⚠️ Sorry babe, couldn't reach the AI right now."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(generate_ai_response(update.message.text))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)
