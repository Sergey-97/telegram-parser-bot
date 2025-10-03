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

📊 **Логика работы:**
• Парсим только новые посты (без дублирования)
• Берем последние 5 постов из основных каналов
• Анализируем релевантные обсуждения
• Формируем ежедневный обзор

⚡ **Команды:**
/start - показать это сообщение
/test - тестовая команда
/status - показать статус бота
/channels - показать список каналов
/parse - запустить парсинг вручную
/stats - статистика базы данных

Бот работает на Render.com и доступен 24/7!
    """
    await update.message.reply_text(welcome_text)

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая команда для проверки работы"""
    await update.message.reply_text("✅ Бот работает! Команды обрабатываются корректно.")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статус бота"""
    from database import Session, Post
    session = Session()
    
    try:
        total_posts = session.query(Post).count()
        main_posts = session.query(Post).filter_by(is_main_post=True).count()
        discussion_posts = session.query(Post).filter_by(is_main_post=False).count()
        processed_posts = session.query(Post).filter_by(processed=True).count()
        
        status_text = f"""
📊 **Статус бота:**

• 📡 Исходных каналов: {len(SOURCE_CHANNELS)}
• 💬 Каналов обсуждений: {len(DISCUSSION_CHANNELS)}
• 🎯 Целевой канал: {TARGET_CHANNEL}

📈 **Статистика базы:**
• Всего постов: {total_posts}
• Основных постов: {main_posts}
• Обсуждений: {discussion_posts}
• Обработано: {processed_posts}

• 🌐 Окружение: {'🚀 Production' if os.environ.get('RENDER', False) else '🔧 Development'}
• 🤖 Статус: 🟢 Активен
• 🏥 Health check: 🟢 Работает

Бот успешно запущен и готов к работе!
    """
        await update.message.reply_text(status_text)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при получении статуса: {e}")
    finally:
        session.close()

async def channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список отслеживаемых каналов"""
    channels_text = "📡 **Отслеживаемые каналы:**\n\n"
    
    channels_text += "**🎯 Основные каналы (источники):**\n"
    for i, channel in enumerate(SOURCE_CHANNELS, 1):
        channels_text += f"{i}. {channel}\n"
        
    channels_text += "\n**💬 Каналы обсуждений (анализ):**\n"
    for i, channel in enumerate(DISCUSSION_CHANNELS, 1):
        channels_text += f"{i}. {channel}\n"
        
    channels_text += f"\n**🎯 Целевой канал:** {TARGET_CHANNEL}"
    channels_text += f"\n\n**⚙️ Настройки:**"
    channels_text += f"\n• Макс. постов на канал: {os.environ.get('MAX_POSTS_PER_CHANNEL', '5')}"
    channels_text += f"\n• Интервал парсинга: {os.environ.get('PARSE_INTERVAL_DAYS', '1')} день"
    
    await update.message.reply_text(channels_text)

async def parse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ручной запуск парсинга"""
    await update.message.reply_text("🔄 Запускаю парсинг каналов...")
    
    try:
        from parser import parse_channels_sync
        result = parse_channels_sync()
        await update.message.reply_text(f"✅ Парсинг завершен! Найдено {len(result)} новых постов")
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        await update.message.reply_text(f"❌ Ошибка при парсинге: {e}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает детальную статистику"""
    from database import Session, Post
    from datetime import datetime, timedelta
    
    session = Session()
    
    try:
        # Базовая статистика
        total_posts = session.query(Post).count()
        main_posts = session.query(Post).filter_by(is_main_post=True).count()
        discussion_posts = session.query(Post).filter_by(is_main_post=False).count()
        processed_posts = session.query(Post).filter_by(processed=True).count()
        unprocessed_posts = session.query(Post).filter_by(processed=False).count()
        
        # Посты за последние 24 часа
        yesterday = datetime.now() - timedelta(days=1)
        recent_posts = session.query(Post).filter(Post.created_at >= yesterday).count()
        
        stats_text = f"""
📈 **Детальная статистика:**

**📊 Общая статистика:**
• Всего постов: {total_posts}
• Основных постов: {main_posts}
• Обсуждений: {discussion_posts}
• Обработано: {processed_posts}
• Необработано: {unprocessed_posts}

**🕐 Активность:**
• Постов за 24ч: {recent_posts}

**🎯 Каналы:**
• Основных: {len(SOURCE_CHANNELS)}
• Обсуждений: {len(DISCUSSION_CHANNELS)}

**⚙️ Настройки:**
• Макс. постов: {os.environ.get('MAX_POSTS_PER_CHANNEL', '5')}
• Интервал: {os.environ.get('PARSE_INTERVAL_DAYS', '1')} день
• Время публикации: {os.environ.get('PUBLISH_TIME', '10:00')}
"""
        await update.message.reply_text(stats_text)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при получении статистики: {e}")
    finally:
        session.close()

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
        application.add_handler(CommandHandler("parse", parse_command))
        application.add_handler(CommandHandler("stats", stats_command))
        
        print("=" * 50)
        print("🤖 Telegram Parser Bot запускается...")
        print(f"🎯 Целевой канал: {TARGET_CHANNEL}")
        print(f"📡 Основных каналов: {len(SOURCE_CHANNELS)}")
        print(f"💬 Каналов обсуждений: {len(DISCUSSION_CHANNELS)}")
        print(f"⚙️ Макс. постов на канал: {os.environ.get('MAX_POSTS_PER_CHANNEL', '5')}")
        print("=" * 50)
        
        logger.info("🤖 Бот запускается...")
        
        # Запускаем планировщик
        try:
            from scheduler import run_scheduler_in_thread
            scheduler = run_scheduler_in_thread()
            print("✅ Планировщик запущен")
        except Exception as e:
            print(f"⚠️ Планировщик не запущен: {e}")
        
        # Запускаем бота (блокирующий вызов)
        print("🔄 Запускаем polling...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка запуска бота: {e}")
        print(f"❌ Критическая ошибка запуска бота: {e}")

if __name__ == '__main__':
    main()