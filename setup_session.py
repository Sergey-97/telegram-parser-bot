import asyncio
import os
from pyrogram import Client
from config import API_ID, API_HASH

async def create_user_session():
    """Создает пользовательскую сессию для парсинга"""
    print("🔐 Создание пользовательской сессии...")
    
    client = Client(
        "telegram_user",  # Изменим название сессии
        api_id=API_ID,
        api_hash=API_HASH,
        workdir="."
    )
    
    try:
        await client.start()
        print("✅ Пользовательская сессия создана!")
        
        # Проверяем соединение
        me = await client.get_me()
        print(f"✅ Вошли как: {me.first_name} (@{me.username})")
        print("✅ Теперь можно парсить каналы!")
        
        await client.stop()
        print("✅ Файл сессии создан: telegram_user.session")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(create_user_session())