import os
import telebot
import yt_dlp
import uuid
from telebot import types

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

user_links = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👹 MONSTER DOWNLOADER v2.0\n\nLink yuboring, videoni va musiqasini yuklab beraman!")

@bot.message_handler(func=lambda m: "http" in m.text)
def handle_video(message):
    url = message.text
    chat_id = message.chat.id
    user_links[chat_id] = url
    
    m_status = bot.reply_to(message, "⏳ Tayyorlanmoqda...")
    
    # Har safar yangi va noyob nom yaratamiz
    unique_id = str(uuid.uuid4())[:8]
    filename = f"video_{unique_id}.mp4"
    
    try:
        ydl_opts = {
            'outtmpl': filename,
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            # Instagram bloklaridan qochish uchun sozlamalar:
            'referer': 'https://www.instagram.com/',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        markup = types.InlineKeyboardMarkup()
        btn_audio = types.InlineKeyboardButton("🎵 Musiqasini olish (MP3)", callback_data="get_audio")
        markup.add(btn_audio)
        
        with open(filename, 'rb') as v:
            bot.send_video(chat_id, v, caption="✅ Tayyor!", reply_markup=markup)
        
        if os.path.exists(filename):
            os.remove(filename)
        bot.delete_message(chat_id, m_status.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Xato: Instagram/TikTok hozircha rad etdi. Birozdan keyin urinib ko'ring yoki boshqa link tashlang.", chat_id, m_status.message_id)
        if os.path.exists(filename):
            os.remove(filename)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    
    if call.data == "get_audio" and url:
        bot.answer_callback_query(call.id, "⏳ Musiqa tayyorlanmoqda...")
        unique_id = str(uuid.uuid4())[:8]
        audio_filename = f"audio_{unique_id}"
        
        try:
            ydl_opts_audio = {
                'outtmpl': audio_filename,
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                ydl.download([url])
            
            full_audio_name = audio_filename + ".mp3"
            with open(full_audio_name, 'rb') as a:
                bot.send_audio(chat_id, a, caption="🎵 Mana videodagi musiqa!")
            
            if os.path.exists(full_audio_name):
                os.remove(full_audio_name)
        except:
            bot.send_message(chat_id, "❌ Musiqani ajratib bo'lmadi.")

bot.infinity_polling()
