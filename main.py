import os
import telebot
import yt_dlp
import google.generativeai as genai

# Kalitlarni Railway'dan olamiz
TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY") # Endi Gemini kaliti

# Gemini AI ni sozlash
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👹 VIP BEPUL AI BOT ISHGA TUSHDI.\n\nMenga xohlagan savolingizni bering yoki video link yuboring!")

@bot.message_handler(func=lambda m: "http" in m.text)
def handle_links(message):
    url = message.text
    m_status = bot.reply_to(message, "⏳ Video tahlil qilinmoqda va yuklanmoqda...")
    try:
        ydl_opts = {'outtmpl': 'video.mp4', 'format': 'best', 'quiet': True, 'max_filesize': 45*1024*1024}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open('video.mp4', 'rb') as v:
            bot.send_video(message.chat.id, v, caption="👹 Tayyor!")
        os.remove('video.mp4')
        bot.delete_message(message.chat.id, m_status.message_id)
    except:
        bot.edit_message_text("❌ Linkdan video yuklab bo'lmadi yoki video juda katta.", message.chat.id, m_status.message_id)

@bot.message_handler(func=lambda m: True)
def chat_ai(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except:
        bot.reply_to(message, "🤖 AI hozircha band, birozdan keyin yozib ko'ring.")

bot.infinity_polling()
