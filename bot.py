import os
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from dotenv import load_dotenv
import requests

# Настройка логгирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка токенов
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENROUTER_KEY = os.getenv('OPENROUTER_API_KEY')

# Доступные модели нейросетей
MODELS = {
    "gpt-3.5-turbo": "OpenAI ChatGPT",
    "claude-3-sonnet": "Anthropic Claude",
    "llama3-70b": "Meta Llama 3"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = (
        "🧠 *Нейро-бот активирован!*\n\n"
        "Доступные модели:\n"
        + "\n".join([f"- {name} (`{key}`)" for key, name in MODELS.items()]) +
        "\n\nПросто напишите сообщение, и я отвечу!"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка всех текстовых сообщений"""
    user_text = update.message.text
    
    try:
        # Выбираем модель (можно сделать выбор через команды)
        model = "gpt-3.5-turbo"
        
        # Запрос к OpenRouter API
        headers = {
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "HTTP-Referer": "https://github.com",
            "X-Title": "NeuroBot"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": user_text}],
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        # Проверяем статус ответа
        response.raise_for_status()
        
        # Получаем ответ ИИ
        ai_response = response.json()['choices'][0]['message']['content']
        
        # Отправляем пользователю (обрезаем до 4000 символов)
        await update.message.reply_text(ai_response[:4000])
        
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        await update.message.reply_text("⚠️ Произошла ошибка. Попробуйте позже.")

def main():
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("Бот запущен и ожидает сообщений...")
    app.run_polling()

if __name__ == "__main__":
    main()
