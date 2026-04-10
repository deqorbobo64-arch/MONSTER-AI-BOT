import os
import telebot
import yt_dlp
from telebot import types

TOKEN = os.getenv("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Vaqtinchalik linklarni saqlash
user_links = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "👹 VIP MONSTER DOWNLOADER!\n\nLink yuboring, men uni darrov yuklab beraman!")

@bot.message_handler(func=lambda m: "http" in m.text)
def handle_video_download(message):
    url = message.text
    chat_id = message.chat.id
    user_links[chat_id] = url # Linkni eslab qolamiz
    
    m_status = bot.reply_to(message, "⏳ Video yuklanmoqda...")
    
    try:
        # Birinchi bo'lib videoni yuklab olamiz
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'format': 'best',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        # Tugmalarni yaratamiz
        markup = types.InlineKeyboardMarkup()
        btn_audio = types.InlineKeyboardButton("🎵 Musiqasini olish (MP3)", callback_data="get_audio")
        btn_full_video = types.InlineKeyboardButton("🎬 To'liq klipni olish", callback_data="get_video")
        markup.add(btn_audio, btn_full_video)
        
        # Videoni yuboramiz va tagida tugmalarni chiqaramiz
        with open(filename, 'rb') as v:
            bot.send_video(chat_id, v, caption="✅ Video yuklab berildi!\n\nNima qilishni tanlang:", reply_markup=markup)
        
        # Faylni serverdan o'chiramiz
        os.remove(filename)
        bot.delete_message(chat_id, m_status.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Xato: Videoni yuklab bo'lmadi.", chat_id, m_status.message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_extra_files(call):
    chat_id = call.message.chat.id
    url = user_links.get(chat_id)
    
    if not url:
        bot.answer_callback_query(call.id, "❌ Link muddati o'tgan.")
        return

    bot.answer_callback_query(call.id, "⏳ Tayyorlanmoqda...")

    try:
        if call.data == "get_audio":
            # Musiqani MP3 qilib yuklash
            ydl_opts_audio = {
                'outtmpl': '%(title)s.%(ext)s',
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
                info = ydl.extract_info(url, download=True)
                audio_file = ydl.prepare_filename(info).rsplit('.', 1)[0] + ".mp3"
            
            with open(audio_file, 'rb') as a:
                bot.send_audio(chat_id, a, caption="🎵 Mana videodagi musiqa!")
            os.remove(audio_file)

        elif call.data == "get_video":
            # Xuddi shu videoni qaytadan (yoki boshqa sifatda) yuborish
            # Bu yerda klipni qayta yuboramiz
            bot.send_message(chat_id, "🎬 Klip yuqorida yuklab berildi. Agar boshqa sifat kerak bo'lsa, linkni qayta yuboring.")

    except Exception as e:
        bot.send_message(chat_id, "❌ Faylni yuklashda xatolik yuz berdi.")

bot.infinity_polling()
