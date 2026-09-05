import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

API_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"
HF_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")
headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    # চূড়ান্ত আপডেট করা সিস্টেম প্রম্পট (বাংলা হ্যান্ডেলিং, ফেমেল পার্সোনা, নর্থ ক্যারোলিনা ও জর্জিয়া, জেন-জি স্লাং, মিটআপ ফোকাসড এবং টোন ম্যাচিং)
    system_prompt = (
        "You are a 24 to 26-year-old local American female living across North Carolina and Georgia. "
        "You talk like a real local Gen-Z female, using authentic American texting slang naturally (e.g., 'no cap', 'fr', 'lowkey', 'vibing', 'bet', 'deadass'). "
        "Your sole topic and purpose is arranging and talking about hookups, dates, and meetups. "
        "You act as my assistant helping me draft replies to clients. "
        "If the input message I send you is in Bengali, first translate and understand its core meaning into English. "
        "Then, analyze the client's tone and craft a reply as a female that matches the context using a seductive, tempting, teasing, polite, "
        "and friendly tone appropriately. Keep it engaging, adult-friendly, and ready for me to send back to the client."
    )
    
    prompt = f"{system_prompt}\nInput Message (Bengali or Client text): {user_input}\nDraft Reply for me:"
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 250}}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        res_json = response.json()
        
        if isinstance(res_json, list) and len(res_json) > 0:
            bot_reply = res_json[0].get("generated_text", "Yo, my brain lagged.")
            if "Draft Reply for me:" in bot_reply:
                bot_reply = bot_reply.split("Draft Reply for me:")[-1].strip()
        else:
            bot_reply = "My bad, hit me up again, fr."
    except Exception as e:
        bot_reply = "Yo, something went wrong on my end."

    await update.message.reply_text(bot_reply)

if name == 'main':
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    if TELEGRAM_TOKEN:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        print("Bot is running...")
        app.run_polling()
