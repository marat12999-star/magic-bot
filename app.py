import os
import telebot
import requests
import io
from flask import Flask
from threading import Thread

TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# Функция для перевода русского текста на английский
def translate_to_english(text):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=en&dt=t&q={requests.utils.quote(text)}"
        response = requests.get(url).json()
        translated_text = "".join([sentence[0] for sentence in response[0]])
        return translated_text
    except Exception:
        return text # Если перевод не удался, отправляем как есть

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'Привет! 👋 Я бот-художник.\nОтправь мне любой текст (промпт), и я нарисую картинку!')

@bot.message_handler(content_types=['text'])
def generate_image(message):
    prompt = message.text
    bot.reply_to(message, '🎨 Анализирую запрос и рисую, подожди 10-15 секунд...')
    
    # Переводим запрос на английский для лучшего результата
    english_prompt = translate_to_english(prompt)
    print(f"Оригинал: {prompt} | Перевод: {english_prompt}") # Выведем в логи для проверки
    
    # Отправляем английскую версию в нейросеть
    image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(english_prompt)}?width=1024&height=1024&model=flux&nologo=true"
    
    try:
        response = requests.get(image_url, timeout=60)
        response.raise_for_status()
        image_bytes = io.BytesIO(response.content)
        bot.send_photo(message.chat.id, image_bytes, caption=f'Готово! Твой промпт: {prompt}\n(В оригинале: {english_prompt})')
    except Exception as e:
        bot.reply_to(message, f'😔 Ошибка: {e}. Попробуй еще раз.')

def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    t = Thread(target=run_bot)
    t.start()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
