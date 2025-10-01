from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import BOT_TOKEN, TARGET_CHANNEL, SOURCE_CHANNELS, DISCUSSION_CHANNELS
import asyncio
import os
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),  # Вывод в консоль
        logging.FileHandler('bot.log', encoding='utf-8')  # Запись в файл
    ]
)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Обработчик команды /start\"\"\"
    user = update.effective_user
    welcome_text = f\"\"\"
 Привет, {user.first_name}!

Я - бот для автоматического парсинга и публикации постов из Telegram каналов.

 **Мои возможности:**
 Парсинг каналов по расписанию
 Анализ контента через нейросети
 Автоматическая публикация обзоров

 **Команды:**
/start - показать это сообщение
/parse - запустить парсинг вручную
/publish - опубликовать пост вручную
/status - показать статус бота
/logs - показать последние логи
/channels - показать список каналов

Бот работает на Render.com и доступен 24/7!
    \"\"\"
    await update.message.reply_text(welcome_text)

async def parse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Ручной запуск парсинга\"\"\"
    await update.message.reply_text(\" Запускаю парсинг каналов...\")
    
    try:
        from parser import parse_channels_sync
        result = parse_channels_sync()
        await update.message.reply_text(f\" Парсинг завершен! Найдено {len(result)} постов\")
    except Exception as e:
        logger.error(f\"Ошибка при парсинге: {e}\")
        await update.message.reply_text(f\" Ошибка при парсинге: {e}\")

async def publish_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Ручная публикация поста\"\"\"
    await update.message.reply_text(\" Подготавливаю и публикую пост...\")
    
    try:
        from scheduler import BotScheduler
        scheduler = BotScheduler()
        scheduler.process_and_publish()
        await update.message.reply_text(\" Пост обработан успешно! (публикация временно отключена)\")
    except Exception as e:
        logger.error(f\"Ошибка при публикации: {e}\")
        await update.message.reply_text(f\" Ошибка при публикации: {e}\")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Показывает статус бота\"\"\"
    try:
        from database import Session, Post
        session = Session()
        
        # Получаем статистику
        new_posts = session.query(Post).filter(Post.processed == False).count()
        processed_posts = session.query(Post).filter(Post.processed == True).count()
        last_post = session.query(Post).order_by(Post.created_at.desc()).first()
        
        # Информация о каналах
        source_count = len(SOURCE_CHANNELS)
        discussion_count = len(DISCUSSION_CHANNELS)
        
        session.close()
        
        status_text = f\"\"\"
 **Статус бота:**

  Новых постов: {new_posts}
  Обработанных постов: {processed_posts}
  Последнее обновление: {last_post.created_at.strftime('%Y-%m-%d %H:%M') if last_post else 'Нет данных'}
        
  Исходных каналов: {source_count}
  Каналов обсуждений: {discussion_count}
  Целевой канал: {TARGET_CHANNEL}

  Окружение: {' Production' if os.environ.get('RENDER', False) else ' Development'}
  Планировщик:  Временно отключен
        \"\"\"
        
        await update.message.reply_text(status_text)
        
    except Exception as e:
        logger.error(f\"Ошибка при получении статуса: {e}\")
        await update.message.reply_text(f\" Ошибка при получении статуса: {e}\")

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Показывает последние логи\"\"\"
    try:
        if not os.path.exists('bot.log'):
            await update.message.reply_text(\" Файл логов еще не создан\")
            return
            
        with open('bot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
            log_lines = lines[-15:]  # Последние 15 строк
        
        log_text = \" **Последние логи:**\\n\\n\" + \"\".join(log_lines) if log_lines else \"Логи пока пусты\"
        
        # Обрезаем если слишком длинный
        if len(log_text) > 4000:
            log_text = log_text[:4000] + \"\\n... (логи обрезаны)\"
            
        await update.message.reply_text(f\"`\\n{log_text}\\n`\", parse_mode='MarkdownV2')
        
    except Exception as e:
        logger.error(f\"Ошибка при чтении логов: {e}\")
        await update.message.reply_text(f\" Ошибка при чтении логов: {e}\")

async def channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    \"\"\"Показывает список отслеживаемых каналов\"\"\"
    try:
        channels_text = \" **Отслеживаемые каналы:**\\n\\n\"
        
        channels_text += \"** Основные каналы:**\\n\"
        for i, channel in enumerate(SOURCE_CHANNELS, 1):
            channels_text += f\"{i}. {channel}\\n\"
            
        channels_text += \"\\n** Каналы обсуждений:**\\n\"
        for i, channel in enumerate(DISCUSSION_CHANNELS, 1):
            channels_text += f\"{i}. {channel}\\n\"
            
        channels_text += f\"\\n** Целевой канал:** {TARGET_CHANNEL}\"
        
        await update.message.reply_text(channels_text)
        
    except Exception as e:
        logger.error(f\"Ошибка при показе каналов: {e}\")
        await update.message.reply_text(f\" Ошибка при показе каналов: {e}\")

def main():
    \"\"\"Основная функция запуска бота\"\"\"
    # Проверяем обязательные переменные окружения
    required_vars = ['API_ID', 'API_HASH', 'BOT_TOKEN']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        error_msg = f\" Отсутствуют обязательные переменные окружения: {missing_vars}\"
        logger.error(error_msg)
        print(error_msg)
        print(\"Пожалуйста, установите их в настройках Render.com\")
        return
    
    # Создаем приложение бота
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler(\"start\", start_command))
    application.add_handler(CommandHandler(\"parse\", parse_command))
    application.add_handler(CommandHandler(\"publish\", publish_command))
    application.add_handler(CommandHandler(\"status\", status_command))
    application.add_handler(CommandHandler(\"logs\", logs_command))
    application.add_handler(CommandHandler(\"channels\", channels_command))
    
    # ВРЕМЕННО ОТКЛЮЧАЕМ ПЛАНИРОВЩИК чтобы избежать циклических импортов
    # scheduler = run_scheduler_in_thread()
    
    logger.info(\" Бот запущен на Render...\")
    print(\"=\" * 50)
    print(\" Telegram Parser Bot запущен и готов к работе!\")
    print(f\" Целевой канал: {TARGET_CHANNEL}\")
    print(f\" Исходных каналов: {len(SOURCE_CHANNELS)}\")
    print(f\" Каналов обсуждений: {len(DISCUSSION_CHANNELS)}\")
    print(\"=\" * 50)
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
