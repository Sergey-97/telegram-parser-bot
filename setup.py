import asyncio
import os
from pyrogram import Client
from config import API_ID, API_HASH

async def setup_telegram():
    """Настройка Telegram клиента"""
    print("🔐 Настройка Telegram клиента...")
    
    client = Client("telegram_parser", api_id=API_ID, api_hash=API_HASH)
    
    try:
        await client.start()
        print("✅ Сессия успешно создана!")
        
        # Проверяем соединение
        me = await client.get_me()
        print(f"✅ Вошли как: {me.first_name} (@{me.username})")
        
        await client.stop()
        print("✅ Настройка завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка настройки: {e}")

if __name__ == "__main__":
    asyncio.run(setup_telegram())