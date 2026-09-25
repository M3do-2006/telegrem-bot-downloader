FROM python:3.10-slim

# تثبيت أدوات النظام و FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

# نسخ ملفات البوت
COPY . /app

# تثبيت مكتبات بايثون
RUN pip install --no-cache-dir pyTelegramBotAPI yt-dlp

# تشغيل البوت
CMD ["python", "bot.py"]
