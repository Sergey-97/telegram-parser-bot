import os
import asyncio
import logging
from pyrogram import Client
from config import API_ID, API_HASH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_session():
    """Проверяет какая сессия используется"""
    print("🔍 Проверка сессии на Render...")
    
    # Проверяем файлы
    files = os.listdir('.')
    session_files = [f for f in files if f.endswith('.session')]
    print(f"📁 Файлы сессии: {session_files}")
    
    # Пробуем подключиться с пользовательской сессией
    if 'telegram_parser.session' in session_files:
        print("🔐 Пробуем подключиться с telegram_parser.session...")
        try:
            client = Client("telegram_parser", API_ID, API_HASH)
            await client.start()
            me = await client.get_me()
            print(f"✅ Пользовательская сессия: {me.first_name} (@{me.username}) - {me.is_bot}")
            await client.stop()
        except Exception as e:
            print(f"❌ Ошибка пользовательской сессии: {e}")
    
    # Пробуем подключиться как бот
    print("🤖 Пробуем подключиться как бот...")
    try:
        from config import BOT_TOKEN
        if BOT_TOKEN:
            client = Client("bot_test", API_ID, API_HASH, bot_token=BOT_TOKEN)
            await client.start()
            me = await client.get_me()
            print(f"✅ Бот сессия: {me.first_name} (@{me.username}) - {me.is_bot}")
            await client.stop()
    except Exception as e:
        print(f"❌ Ошибка бот сессии: {e}")

if __name__ == "__main__":
    asyncio.run(check_session())