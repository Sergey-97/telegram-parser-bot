# bot_simple.py
import asyncio
import logging
from telethon import TelegramClient
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Упрощенная версия бота для проверки"""
    try:
        # Загружаем конфигурацию
        API_ID = int(os.getenv('API_ID'))
        API_HASH = os.getenv('API_HASH')
        BOT_TOKEN = os.getenv('BOT_TOKEN')
        TARGET_CHANNEL = os.getenv('TARGET_CHANNEL', '@mar_factor')
        
        print("🔧 Загружена конфигурация:")
        print(f"   API_ID: {API_ID}")
        print(f"   BOT_TOKEN: {BOT_TOKEN[:15]}...")
        print(f"   TARGET_CHANNEL: {TARGET_CHANNEL}")
        
        # Создаем клиента
        client = TelegramClient('bot_session', API_ID, API_HASH)
        
        # Запускаем бота
        await client.start(bot_token=BOT_TOKEN)
        
        me = await client.get_me()
        print(f"✅ Бот запущен: {me.first_name} (@{me.username})")
        
        # Пробуем отправить тестовое сообщение
        try:
            channel = await client.get_entity(TARGET_CHANNEL)
            await client.send_message(
                channel, 
                "🤖 Бот перезапущен и работает корректно!\n"
                "AI-парсер готов к работе."
            )
            print(f"✅ Тестовое сообщение отправлено в {TARGET_CHANNEL}")
        except Exception as e:
            print(f"⚠️ Не удалось отправить сообщение: {e}")
        
        print("🎯 Бот готов к работе!")
        print("⏹️  Нажмите Ctrl+C для остановки")
        
        # Ожидаем остановки
        await asyncio.Future()
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Бот остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")