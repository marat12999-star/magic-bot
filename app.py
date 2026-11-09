import os
import telebot
import requests
import io
from flask import Flask
from threading import Thread

TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Простой веб-сервер, чтобы Render не ругался
@app.route('/')
def index():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Привет! 👋 Я бот-художник.\nОтправь мне любой текст (промпт), и я нарисую картинку!')

@bot.message_handler(content_types=['text'])
def generate_image(message):
    prompt = message.text
    bot.reply_to(message, '🎨 Рисую, подожди 10-15 секунд...')
    image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1024&height=1024&model=flux&nologo=true"
    try:
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        image_bytes = io.BytesIO(response.content)
        bot.send_photo(message.chat.id, image_bytes, caption=f'Готово! Твой промпт: {prompt}')
    except Exception as e:
        bot.reply_to(message, f'😔 Ошибка: {e}. Попробуй еще раз.')

def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    # Запускаем бота в отдельном потоке
    t = Thread(target=run_bot)
    t.start()
    # Запускаем веб-сервер на порту, который даст Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)