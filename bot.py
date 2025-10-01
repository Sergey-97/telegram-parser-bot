from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import BOT_TOKEN, TARGET_CHANNEL
from scheduler import run_scheduler_in_thread
import asyncio
import sqlite3
import os
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальная переменная для планировщика
scheduler = None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🤖 Бот для парсинга и публикации постов активирован!\n\n"
        "Команды:\n"
        "/start - показать это сообщение\n"
        "/parse - запустить парсинг вручную\n"
        "/publish - опубликовать пост вручную\n"
        "/status - показать статус бота\n"
        "/logs - показать последние логи"
    )

async def parse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ручной запуск парсинга"""
    await update.message.reply_text("🔄 Запускаю парсинг каналов...")
    
    try:
        from parser import parse_channels_sync
        result = parse_channels_sync()
        await update.message.reply_text(f"✅ Парсинг завершен! Найдено {len(result) if result else 0} постов")
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        await update.message.reply_text(f"❌ Ошибка при парсинге: {e}")

async def publish_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ручная публикация поста"""
    await update.message.reply_text("🔄 Подготавливаю и публикую пост...")
    
    try:
        from scheduler import BotScheduler
        scheduler = BotScheduler()
        scheduler.process_and_publish()
        await update.message.reply_text("✅ Пост опубликован успешно!")
    except Exception as e:
        logger.error(f"Ошибка при публикации: {e}")
        await update.message.reply_text(f"❌ Ошибка при публикации: {e}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает статус бота"""
    try:
        from database import Session, Post
        session = Session()
        
        # Получаем статистику
        new_posts = session.query(Post).filter(Post.processed == False).count()
        processed_posts = session.query(Post).filter(Post.processed == True).count()
        last_post = session.query(Post).order_by(Post.created_at.desc()).first()
        
        session.close()
        
        status_text = (
            "📊 **Статус бота:**\n\n"
            f"• Новых постов: {new_posts}\n"
            f"• Обработанных постов: {processed_posts}\n"
            f"• Последний пост: {last_post.created_at if last_post else 'Нет данных'}\n"
            f"• Целевой канал: {TARGET_CHANNEL}\n"
            f"• Окружение: {'Production' if os.environ.get('RENDER', False) else 'Development'}\n"
            f"• Планировщик: {'🟢 Активен' if scheduler else '🔴 Неактивен'}"
        )
        
        await update.message.reply_text(status_text)
        
    except Exception as e:
        logger.error(f"Ошибка при получении статуса: {e}")
        await update.message.reply_text(f"❌ Ошибка при получении статуса: {e}")

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает последние логи"""
    try:
        # Читаем последние строки из логов
        log_lines = []
        if os.path.exists('bot.log'):
            with open('bot.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                log_lines = lines[-10:]  # Последние 10 строк
        
        log_text = "📋 **Последние логи:**\n\n" + "".join(log_lines) if log_lines else "Логи пока пусты"
        
        # Обрезаем если слишком длинный
        if len(log_text) > 4000:
            log_text = log_text[:4000] + "..."
            
        await update.message.reply_text(f"```\n{log_text}\n```", parse_mode='MarkdownV2')
        
    except Exception as e:
        logger.error(f"Ошибка при чтении логов: {e}")
        await update.message.reply_text(f"❌ Ошибка при чтении логов: {e}")

async def publish_post(content):
    """Публикует пост в целевой канал"""
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        await application.bot.send_message(
            chat_id=TARGET_CHANNEL,
            text=content,
            parse_mode='Markdown'
        )
        logger.info(f"Пост опубликован в канал {TARGET_CHANNEL}")
        
    except Exception as e:
        logger.error(f"Ошибка при публикации поста: {e}")

def main():
    """Основная функция запуска бота"""
    # Проверяем обязательные переменные окружения
    required_vars = ['API_ID', 'API_HASH', 'BOT_TOKEN']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Отсутствуют обязательные переменные окружения: {missing_vars}")
        print(f"ERROR: Missing required environment variables: {missing_vars}")
        return
    
    # Инициализируем базу данных
    try:
        from migrate_db import setup_database
        setup_database()
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("parse", parse_command))
    application.add_handler(CommandHandler("publish", publish_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("logs", logs_command))
    
    # Запускаем планировщик в отдельном потоке
    global scheduler
    scheduler = run_scheduler_in_thread()
    
    logger.info("Бот запущен на Render...")
    print("🤖 Бот запущен и готов к работе!")
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()