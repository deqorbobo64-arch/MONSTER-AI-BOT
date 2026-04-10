import os
import telebot
import yt_dlp
from g4f.client import Client

# Kalit faqat Telegram uchun kerak
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TOKEN)
ai_client = Client()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👹 VIP FREE AI BOT TAYYOR!\n\nMenga xohlagan savolingizni bering yoki video link yuboring.")

@bot.message_handler(func=lambda m: "http" in m.text)
def handle_links(message):
    url = message.text
    m_status = bot.reply_to(message, "⏳ Video yuklanmoqda...")
    try:
        ydl_opts = {'outtmpl': 'video.mp4', 'format': 'best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open('video.mp4', 'rb') as v:
            bot.send_video(message.chat.id, v, caption="👹 Tayyor!")
        os.remove('video.mp4')
        bot.delete_message(message.chat.id, m_status.message_id)
    except:
        bot.edit_message_text("❌ Video yuklashda xato.", message.chat.id, m_status.message_id)

@bot.message_handler(func=lambda m: True)
def chat_ai(message):
    try:
        response = ai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}]
        )
        bot.reply_to(message, response.choices[0].message.content)
    except:
        bot.reply_to(message, "🤖 AI hozircha javob berolmaydi, birozdan keyin yozing.")

bot.infinity_polling()
