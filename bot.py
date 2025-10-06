import asyncio
import logging
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
import config
from database import init_db, save_message, get_last_parsed_date
from parser import parse_channel_messages
import schedule
import time
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация клиента Telegram
client = TelegramClient(
    'parser_bot_session',
    config.API_ID,
    config.API_HASH
)

async def publish_to_channel(message_text, media=None):
    """Публикует сообщение в целевой канал"""
    try:
        channel = await client.get_entity(config.TARGET_CHANNEL)
        if media:
            await client.send_file(channel, media, caption=message_text)
        else:
            await client.send_message(channel, message_text)
        logger.info(f"✅ Сообщение опубликовано в {config.TARGET_CHANNEL}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка публикации: {e}")
        return False

async def parse_and_publish():
    """Основная функция парсинга и публикации"""
    logger.info("🔄 Запуск парсинга каналов...")
    
    try:
        # Получаем дату последнего парсинга
        last_parsed = get_last_parsed_date()
        since_date = datetime.now() - timedelta(days=config.PARSE_INTERVAL_DAYS)
        
        if last_parsed and last_parsed > since_date:
            since_date = last_parsed
        
        # Парсим сообщения из исходных каналов
        all_messages = []
        for source_channel in config.SOURCE_CHANNELS:
            try:
                messages = await parse_channel_messages(client, source_channel, since_date)
                all_messages.extend(messages)
                logger.info(f"📥 Получено {len(messages)} сообщений из {source_channel}")
            except Exception as e:
                logger.error(f"❌ Ошибка парсинга {source_channel}: {e}")
        
        # Фильтруем и публикуем сообщения
        published_count = 0
        for message in all_messages:
            # Здесь можно добавить фильтрацию по ключевым словам
            if await publish_to_channel(message.text):
                save_message(
                    message_id=message.id,
                    channel=message.channel,
                    text=message.text,
                    date=message.date,
                    published=True
                )
                published_count += 1
                # Задержка между сообщениями чтобы не спамить
                await asyncio.sleep(2)
        
        logger.info(f"🎉 Парсинг завершен. Опубликовано {published_count} сообщений")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при парсинге: {e}")

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Обработчик команды /start"""
    await event.reply(
        "🤖 Бот-парсер активен!\n\n"
        f"**Целевой канал:** {config.TARGET_CHANNEL}\n"
        f"**Источники:** {', '.join(config.SOURCE_CHANNELS)}\n"
        f"**Интервал парсинга:** {config.PARSE_INTERVAL_DAYS} дней\n\n"
        "**Команды:**\n"
        "/parse - ручной запуск парсинга\n"
        "/status - статус бота"
    )

@client.on(events.NewMessage(pattern='/parse'))
async def parse_handler(event):
    """Ручной запуск парсинга"""
    await event.reply("🔄 Запускаю парсинг...")
    await parse_and_publish()
    await event.reply("✅ Парсинг завершен")

@client.on(events.NewMessage(pattern='/status'))
async def status_handler(event):
    """Показывает статус бота"""
    status_info = (
        f"🤖 **Статус бота:** Активен\n"
        f"👤 **Пользователь:** {(await client.get_me()).first_name}\n"
        f"🎯 **Целевой канал:** {config.TARGET_CHANNEL}\n"
        f"📡 **Источники:** {len(config.SOURCE_CHANNELS)}\n"
        f"⏰ **Интервал:** {config.PARSE_INTERVAL_DAYS} дней\n"
        f"🕒 **Время публикации:** {config.PUBLISH_TIME}"
    )
    await event.reply(status_info)

def run_scheduler():
    """Запускает планировщик для автоматического парсинга"""
    schedule.every().day.at(config.PUBLISH_TIME).do(
        lambda: asyncio.create_task(parse_and_publish())
    )
    
    while True:
        schedule.run_pending()
        time.sleep(1)

async def main():
    """Основная функция бота"""
    try:
        # Инициализация базы данных
        init_db()
        
        # Запуск клиента
        await client.start(bot_token=config.BOT_TOKEN)
        
        me = await client.get_me()
        logger.info(f"✅ Бот запущен: {me.first_name} (@{me.username})")
        logger.info(f"🎯 Целевой канал: {config.TARGET_CHANNEL}")
        logger.info(f"📡 Источники: {config.SOURCE_CHANNELS}")
        
        # Тестовая публикация при запуске
        await publish_to_channel("🚀 Бот-парсер запущен и готов к работе!")
        
        # Запуск планировщика в отдельном потоке
        import threading
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("🤖 Бот работает. Нажмите Ctrl+C для остановки.")
        
        # Ожидание сообщений
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при запуске бота: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("❌ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")