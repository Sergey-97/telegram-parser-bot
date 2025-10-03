from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import BOT_TOKEN, TARGET_CHANNEL, SOURCE_CHANNELS, DISCUSSION_CHANNELS
import os
import logging
import threading
from flask import Flask

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Создаем Flask приложение для health check
app = Flask(__name__)

@app.route('/')
def health_check():
    return {
        'status': 'healthy',
        'service': 'Telegram Parser Bot',
        'message': 'Bot is running successfully!'
    }

@app.route('/status')
def status():
    return {
        'status': 'running',
        'bot': 'active'
    }

@app.route('/ping')
def ping():
    return {'ping': 'pong'}

def run_health_check():
    """Запускает Flask сервер для health check"""
    try:
        print("🏥 Запускаем health check сервер на порту 10000...")
        app.run(host='0.0.0.0', port=10000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Ошибка health check сервера: {e}")

def start_health_check():
    """Запускает health check в отдельном потоке"""
    try:
        health_thread = threading.Thread(target=run_health_check)
        health_thread.daemon = True
        health_thread.start()
        print("✅ Health check сервер запущен")
        return health_thread
    except Exception as e:
        print(f"⚠️ Не удалось запустить health check: {e}")
        return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    welcome_text = f"""
🤖 Привет, {user.first_name}!

Я - бот для автоматического парсинга и публикации постов из Telegram каналов.

📊 **Мои возможности:**
• Парсинг каналов по расписанию
• Анализ контента через нейросети
• Автоматическая публикация обзоров

⚡ **Команды:**
/start - показать это сообщение
/test - тестовая команда
/status - показать статус бота
/channels - показать список каналов

Бот работает на Render.com и доступен 24/7!
    """
    await update.message.reply_text(welcome_text)

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая команда для проверки работы"""
    await update.message.reply_text("✅ Бот работает! Команды обрабатываются корректно.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статус бота"""
    status_text = f"""
📊 **Статус бота:**

• 📡 Исходных каналов: {len(SOURCE_CHANNELS)}
• 💬 Каналов обсуждений: {len(DISCUSSION_CHANNELS)}
• 🎯 Целевой канал: {TARGET_CHANNEL}

• 🌐 Окружение: {'🚀 Production' if os.environ.get('RENDER', False) else '🔧 Development'}
• 🤖 Статус: 🟢 Активен
• 🏥 Health check: 🟢 Работает

Бот успешно запущен и готов к работе!
    """
    await update.message.reply_text(status_text)

async def channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список отслеживаемых каналов"""
    channels_text = "📡 **Отслеживаемые каналы:**\n\n"
    
    channels_text += "**🎯 Основные каналов:**\n"
    for i, channel in enumerate(SOURCE_CHANNELS, 1):
        channels_text += f"{i}. {channel}\n"
        
    channels_text += "\n**💬 Каналы обсуждений:**\n"
    for i, channel in enumerate(DISCUSSION_CHANNELS, 1):
        channels_text += f"{i}. {channel}\n"
        
    channels_text += f"\n**🎯 Целевой канал:** {TARGET_CHANNEL}"
    
    await update.message.reply_text(channels_text)

async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка связи"""
    await update.message.reply_text("🏓 Понг! Бот активен.")

def main():
    """Основная функция запуска"""
    print("🚀 Инициализация Telegram бота...")
    
    # Проверяем обязательные переменные окружения
    required_vars = ['API_ID', 'API_HASH', 'BOT_TOKEN']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        error_msg = f"❌ Отсутствуют обязательные переменные окружения: {missing_vars}"
        print(error_msg)
        print("Пожалуйста, установите их в настройках Render.com")
        return
    
    try:
        # Запускаем health check сервер
        health_thread = start_health_check()
        
        # Создаем приложение бота
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("test", test_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("channels", channels_command))
        application.add_handler(CommandHandler("ping", ping_command))
        
        print("=" * 50)
        print("🤖 Telegram Parser Bot запускается...")
        print(f"🎯 Целевой канал: {TARGET_CHANNEL}")
        print(f"📡 Исходных каналов: {len(SOURCE_CHANNELS)}")
        print(f"💬 Каналов обсуждений: {len(DISCUSSION_CHANNELS)}")
        print("=" * 50)
        
        logger.info("🤖 Бот запускается...")
        
        # Запускаем бота (блокирующий вызов)
        print("🔄 Запускаем polling...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка запуска бота: {e}")
        print(f"❌ Критическая ошибка запуска бота: {e}")

if __name__ == '__main__':
    main()