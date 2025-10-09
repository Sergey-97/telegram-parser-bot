import os
from pyrogram import Client
from config import API_ID, API_HASH

def setup_client():
    """Настраивает и возвращает клиент Telegram"""
    session_name = "telegram_parser"
    
    # Проверяем, есть ли уже сессия
    if os.path.exists(f"{session_name}.session"):
        print("✅ Найдена существующая сессия")
        return Client(session_name, api_id=API_ID, api_hash=API_HASH)
    else:
        print("🔐 Создание новой сессии...")
        return Client(session_name, api_id=API_ID, api_hash=API_HASH)

async def authenticate_client(client):
    """Аутентифицирует клиента"""
    try:
        await client.start()
        print("✅ Успешная аутентификация")
        return True
    except Exception as e:
        print(f"❌ Ошибка аутентификации: {e}")
        return False