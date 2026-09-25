import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp
import os

# التوكن الخاص بك تم وضعه هنا
TOKEN = '8816340597:AAH0tGOhy8Koq7hg9fH0CHCTLKY4dxlTlSc'
bot = telebot.TeleBot(TOKEN)

user_links = {}

@bot.message_handler(func=lambda message: message.text.startswith('http'))
def handle_link(message):
    chat_id = message.chat.id
    user_links[chat_id] = message.text
    
    markup = InlineKeyboardMarkup()
    btn_video = InlineKeyboardButton("🎬 فيديو (أفضل جودة)", callback_data="download_video")
    btn_audio = InlineKeyboardButton("🎵 صوت (MP3)", callback_data="download_audio")
    markup.row(btn_video, btn_audio)
    
    bot.reply_to(message, "اختر الصيغة المطلوبة:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if chat_id not in user_links:
        bot.edit_message_text("انتهت صلاحية الجلسة، يرجى إرسال الرابط مجدداً.", chat_id=chat_id, message_id=message_id)
        return

    url = user_links[chat_id]
    choice = call.data
    
    bot.edit_message_text("⏳ جاري سحب البيانات والتحميل...", chat_id=chat_id, message_id=message_id)

    if choice == "download_video":
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'vid_{chat_id}.%(ext)s',
            'quiet': True,
        }
    elif choice == "download_audio":
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': f'aud_{chat_id}.%(ext)s',
            'quiet': True,
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if choice == "download_audio":
                filename = filename.rsplit('.', 1)[0] + '.mp3'

        bot.edit_message_text("🚀 جاري الرفع إلى تلجرام...", chat_id=chat_id, message_id=message_id)

        with open(filename, 'rb') as file:
            if choice == "download_video":
                bot.send_video(chat_id, file)
            elif choice == "download_audio":
                bot.send_audio(chat_id, file)

        os.remove(filename)
        del user_links[chat_id]
        bot.delete_message(chat_id, message_id)

    except Exception as e:
        bot.edit_message_text("❌ حدث خطأ، قد يكون الرابط خاصاً أو غير مدعوم.", chat_id=chat_id, message_id=message_id)

bot.infinity_polling()
