import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота из переменных окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

# Глобальные переменные для хранения данных
parsed_data = {}
publication_status = {}
user_channels = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
🤖 Добро пожаловать в бота для парсинга и публикации контента!

Доступные команды:
/parse - Начать парсинг контента
/publish - Опубликовать контент
/status - Статус публикаций
/logs - Показать логи
/channels - Управление каналами

Для начала работы добавьте бота в канал как администратора и используйте команду /channels для настройки.
    """
    await update.message.reply_text(welcome_text)

async def parse_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /parse"""
    try:
        # Здесь будет логика парсинга
        # Временная заглушка
        global parsed_data
        parsed_data['last_parse'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        parsed_data['items_count'] = 10  # Примерное количество
        
        await update.message.reply_text(
            f"✅ Парсинг завершен!\n"
            f"📅 Время: {parsed_data['last_parse']}\n"
            f"📊 Найдено элементов: {parsed_data['items_count']}"
        )
        
    except Exception as e:
        logger.error(f"Error in parse_command: {e}")
        await update.message.reply_text("❌ Ошибка при парсинге")

async def publish_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /publish"""
    try:
        if not parsed_data:
            await update.message.reply_text("❌ Сначала выполните парсинг командой /parse")
            return
        
        # Здесь будет логика публикации
        # Временная заглушка
        global publication_status
        publication_status['last_publication'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        publication_status['status'] = 'completed'
        
        await update.message.reply_text(
            f"✅ Публикация завершена!\n"
            f"📅 Время: {publication_status['last_publication']}\n"
            f"📤 Статус: {publication_status['status']}"
        )
        
    except Exception as e:
        logger.error(f"Error in publish_command: {e}")
        await update.message.reply_text("❌ Ошибка при публикации")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /status"""
    status_text = "📊 Статус системы:\n\n"
    
    if parsed_data:
        status_text += f"📅 Последний парсинг: {parsed_data.get('last_parse', 'Не выполнялся')}\n"
        status_text += f"📊 Элементов: {parsed_data.get('items_count', 0)}\n"
    else:
        status_text += "📅 Парсинг еще не выполнялся\n"
    
    if publication_status:
        status_text += f"\n📤 Последняя публикация: {publication_status.get('last_publication', 'Не выполнялась')}\n"
        status_text += f"🟢 Статус: {publication_status.get('status', 'Неизвестен')}\n"
    else:
        status_text += "\n📤 Публикация еще не выполнялась\n"
    
    status_text += f"\n📈 Каналов настроено: {len(user_channels)}"
    
    await update.message.reply_text(status_text)

async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /logs"""
    try:
        # Здесь будет логика показа логов
        # Временная заглушка
        log_info = f"""
📋 Последние действия:

🕒 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Бот запущен
🕒 {parsed_data.get('last_parse', 'Не выполнялся')} - Парсинг
🕒 {publication_status.get('last_publication', 'Не выполнялась')} - Публикация

Для полных логов проверьте логи сервера.
        """
        await update.message.reply_text(log_info)
        
    except Exception as e:
        logger.error(f"Error in logs_command: {e}")
        await update.message.reply_text("❌ Ошибка при получении логов")

async def channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /channels"""
    try:
        user_id = update.effective_user.id
        
        if context.args:
            # Добавление канала
            channel_id = context.args[0]
            user_channels[user_id] = user_channels.get(user_id, [])
            user_channels[user_id].append(channel_id)
            
            await update.message.reply_text(
                f"✅ Канал {channel_id} добавлен!\n"
                f"📊 Всего каналов: {len(user_channels[user_id])}"
            )
        else:
            # Показать текущие каналы
            if user_id in user_channels and user_channels[user_id]:
                channels_list = "\n".join([f"📢 {channel}" for channel in user_channels[user_id]])
                await update.message.reply_text(
                    f"📋 Ваши каналы:\n{channels_list}\n\n"
                    f"Чтобы добавить канал, используйте: /channels <channel_id>"
                )
            else:
                await update.message.reply_text(
                    "📋 У вас нет добавленных каналов.\n\n"
                    "Чтобы добавить канал, используйте:\n"
                    "/channels <channel_id>\n\n"
                    "Где <channel_id> - ID вашего канала"
                )
                
    except Exception as e:
        logger.error(f"Error in channels_command: {e}")
        await update.message.reply_text("❌ Ошибка при работе с каналами")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка при обработке запроса. Попробуйте позже."
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик неизвестных команд"""
    await update.message.reply_text(
        "❌ Неизвестная команда.\n\n"
        "Доступные команды:\n"
        "/start - Начало работы\n"
        "/parse - Парсинг контента\n"
        "/publish - Публикация\n"
        "/status - Статус\n"
        "/logs - Логи\n"
        "/channels - Управление каналами"
    )

def main():
    """Основная функция запуска бота"""
    try:
        # Создание приложения бота
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("parse", parse_command))
        application.add_handler(CommandHandler("publish", publish_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("logs", logs_command))
        application.add_handler(CommandHandler("channels", channels_command))
        
        # Обработчик неизвестных команд
        application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
        
        # Обработчик ошибок
        application.add_error_handler(error_handler)
        
        # Запуск бота
        logger.info("Бот запускается...")
        print("🤖 Бот запущен! Нажмите Ctrl+C для остановки.")
        
        # Запуск в режиме polling
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        print(f"❌ Ошибка запуска бота: {e}")

if __name__ == "__main__":
    main()