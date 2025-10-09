#!/usr/bin/env python3
"""
Скрипт для первого запуска и настройки бота на Render
"""
import os
import asyncio
from pyrogram import Client
from config import API_ID, API_HASH

async def setup_telegram():
    """Настройка Telegram сессии"""
    print("🔐 Настройка Telegram клиента...")
    
    client = Client(
        "telegram_parser",
        api_id=API_ID,
        api_hash=API_HASH,
        workdir="./"
    )
    
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
        raise

if __name__ == "__main__":
    # Проверяем обязательные переменные
    required_vars = ['API_ID', 'API_HASH']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные: {missing_vars}")
        print("Добавьте их в Environment Variables в Render")
        exit(1)
    
    asyncio.run(setup_telegram())