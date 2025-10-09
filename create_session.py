import asyncio
import os
from pyrogram import Client
from config import API_ID, API_HASH

async def create_session():
    """Создает сессию Telegram"""
    print("🔐 Создание Telegram сессии...")
    
    client = Client(
        "telegram_parser",
        api_id=API_ID,
        api_hash=API_HASH,
        workdir="."
    )
    
    try:
        await client.start()
        print("✅ Сессия успешно создана!")
        
        # Проверяем соединение
        me = await client.get_me()
        print(f"✅ Вошли как: {me.first_name} (@{me.username})")
        
        await client.stop()
        print("✅ Файл сессии создан: telegram_parser.session")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    # Проверяем переменные
    if not API_ID or not API_HASH:
        print("❌ Установите API_ID и API_HASH в config.py или .env файле")
        exit(1)
    
    asyncio.run(create_session())