import os
import telebot
import yt_dlp
from openai import OpenAI

# Kalitlarni Railway "Variables"dan olamiz
TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_KEY)
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👹 VIP MONSTER AI ISHGA TUSHDI.\n\nMenga savol bering yoki video link yuboring!")

@bot.message_handler(func=lambda m: "http" in m.text)
def handle_links(message):
    url = message.text
    m_status = bot.reply_to(message, "⏳ Yuklanmoqda...")
    try:
        ydl_opts = {'outtmpl': 'video.mp4', 'format': 'best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open('video.mp4', 'rb') as v:
            bot.send_video(message.chat.id, v)
        os.remove('video.mp4')
        bot.delete_message(message.chat.id, m_status.message_id)
    except:
        bot.edit_message_text("❌ Linkdan video yuklab bo'lmadi.", message.chat.id, m_status.message_id)

@bot.message_handler(func=lambda m: True)
def chat_ai(message):
    try:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": message.text}]
        )
        bot.reply_to(message, res.choices[0].message.content)
    except:
        bot.reply_to(message, "🤖 AI hozircha javob berolmaydi.")

bot.infinity_polling()
