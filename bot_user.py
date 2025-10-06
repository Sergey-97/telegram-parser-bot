import asyncio
import logging
from telethon import TelegramClient
import config
from database import init_db, save_message
from parser import parse_channel_messages
from ai_processor import AIProcessor
from post_formatter import PostFormatter
from ai_processor_final import AIProcessorFinal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация компонентов
ai_processor = AIProcessorFinal()
post_formatter = PostFormatter()

client = TelegramClient('user_parser_session', config.API_ID, config.API_HASH)

async def publish_to_channel(message_text: str):
    """Публикует структурированное сообщение в канал"""
    try:
        bot_client = TelegramClient('bot_publisher_session', config.API_ID, config.API_HASH)
        await bot_client.start(bot_token=config.BOT_TOKEN)
        
        channel = await bot_client.get_entity(config.TARGET_CHANNEL)
        await bot_client.send_message(channel, message_text)
        
        await bot_client.disconnect()
        logger.info("✅ Структурированный пост опубликован")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка публикации: {e}")
        return False

async def collect_and_process_posts():
    """Собирает и обрабатывает посты через AI"""
    logger.info("🧠 Сбор и AI-обработка постов...")
    
    try:
        # Собираем посты из основных каналов
        main_posts = []
        for source_channel in config.SOURCE_CHANNELS:
            messages = await parse_channel_messages(
                client, source_channel, 
                datetime.now() - timedelta(days=config.PARSE_INTERVAL_DAYS)
            )
            main_posts.extend([msg.text for msg in messages[:5]])  # Берем до 5 постов из каждого
        
        # Собираем посты из дискуссионных каналов
        discussion_posts = []
        for disc_channel in config.DISCUSSION_CHANNELS:
            messages = await parse_channel_messages(
                client, disc_channel,
                datetime.now() - timedelta(days=config.PARSE_INTERVAL_DAYS)
            )
            discussion_posts.extend([msg.text for msg in messages[:10]])
        
        # AI-обработка и структурирование
        structured_content = await ai_processor.structure_content(main_posts, discussion_posts)
        
        # Форматирование поста
        final_post = post_formatter.format_structured_post(
            structured_content, 
            config.SOURCE_CHANNELS + config.DISCUSSION_CHANNELS
        )
        
        return final_post
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки постов: {e}")
        return None

async def parse_and_publish_ai():
    """Основная функция AI-парсинга и публикации"""
    logger.info("🚀 Запуск AI-парсинга...")
    
    try:
        # Собираем и обрабатываем посты
        structured_post = await collect_and_process_posts()
        
        if structured_post and len(structured_post) > 50:  # Проверяем что пост не пустой
            # Публикуем структурированный пост
            success = await publish_to_channel(structured_post)
            if success:
                logger.info("🎉 AI-пост успешно опубликован")
            else:
                logger.error("❌ Не удалось опубликовать AI-пост")
        else:
            logger.warning("⚠️ Недостаточно контента для AI-обработки")
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка AI-парсинга: {e}")

async def main():
    """Основная функция"""
    try:
        init_db()
        await client.start(phone=lambda: input("📱 Введите ваш номер телефона: "))
        
        me = await client.get_me()
        logger.info(f"✅ Пользователь авторизован: {me.first_name}")
        
        # Тестовый AI-парсинг
        await parse_and_publish_ai()
        
        # Можно добавить расписание для автоматического запуска
        logger.info("🤖 AI-парсер готов. Нажмите Ctrl+C для остановки.")
        await asyncio.Future()  # Бесконечное ожидание
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("❌ AI-парсер остановлен")