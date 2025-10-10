import asyncio
import logging
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, SOURCE_CHANNELS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_channel_access():
    """Диагностика доступа к каналам"""
    client = Client(
        "debug_bot", 
        api_id=API_ID, 
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        workdir="./"
    )
    
    try:
        await client.start()
        me = await client.get_me()
        logger.info(f"🤖 Бот: @{me.username} (ID: {me.id})")
        logger.info("=" * 60)
        
        for i, channel_url in enumerate(SOURCE_CHANNELS, 1):
            try:
                # Извлекаем идентификатор канала
                if channel_url.startswith('https://t.me/'):
                    channel_id = channel_url.replace('https://t.me/', '')
                elif channel_url.startswith('@'):
                    channel_id = channel_url[1:]
                else:
                    channel_id = channel_url
                
                logger.info(f"{i}. 🔍 Проверяем: {channel_id}")
                
                # Пробуем получить информацию о канале
                chat = await client.get_chat(channel_id)
                logger.info(f"   📝 Название: {chat.title}")
                logger.info(f"   👥 Участников: {getattr(chat, 'members_count', 'N/A')}")
                logger.info(f"   🔒 Тип: {chat.type}")
                
                # Пробуем получить сообщения
                messages_found = 0
                message_samples = []
                
                async for message in client.get_chat_history(chat.id, limit=5):
                    if message.text and message.text.strip():
                        messages_found += 1
                        if len(message_samples) < 2:
                            message_samples.append(message.text[:100])
                
                logger.info(f"   📨 Найдено сообщений: {messages_found}")
                if message_samples:
                    for j, sample in enumerate(message_samples, 1):
                        logger.info(f"      {j}. {sample}...")
                
                if messages_found == 0:
                    logger.info("   ⚠️  Сообщений не найдено! Возможные причины:")
                    logger.info("      - Канал приватный")
                    logger.info("      - Бот не добавлен в канал")
                    logger.info("      - В канале нет текстовых сообщений")
                
                logger.info("   " + "-" * 40)
                
            except Exception as e:
                logger.error(f"   ❌ Ошибка доступа: {str(e)}")
                logger.info("   ⚠️  Возможные решения:")
                logger.info("      - Добавьте бота в канал как участника")
                logger.info("      - Для приватных каналов нужна пользовательская сессия")
                logger.info("      - Проверьте правильность username канала")
                logger.info("   " + "-" * 40)
        
        logger.info("=" * 60)
        logger.info("💡 РЕКОМЕНДАЦИИ:")
        logger.info("1. Для публичных каналов: убедитесь что username правильный")
        logger.info("2. Для приватных каналов: добавьте бота как участника")
        logger.info("3. Или используйте пользовательскую сессию вместо бота")
        
    except Exception as e:
        logger.error(f"❌ Общая ошибка: {e}")
    finally:
        await client.stop()

if __name__ == "__main__":
    asyncio.run(debug_channel_access())