# check_bot_token.py
import asyncio
from telethon import TelegramClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check_bot_token():
    """Проверяет корректность токена бота"""
    token = os.getenv('BOT_TOKEN')
    
    if not token:
        print("❌ Токен бота не найден в .env")
        print("💡 Добавьте BOT_TOKEN=ваш_токен в файл .env")
        return False
    
    print(f"🔐 Проверяем токен: {token[:15]}...")
    
    try:
        # Используем фиктивные API данные, так как нам нужен только токен
        client = TelegramClient('check_session', 123, 'abc')
        await client.start(bot_token=token)
        
        me = await client.get_me()
        print(f"✅ Токен рабочий! Бот: {me.first_name} (@{me.username})")
        await client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка токена: {e}")
        print("\n💡 Решение:")
        print("1. Откройте @BotFather в Telegram")
        print("2. /mybots → выберите вашего бота")
        print("3. API Token → Revoke current token → Generate new token")
        print("4. Скопируйте новый токен и обновите .env файл")
        return False

if __name__ == "__main__":
    asyncio.run(check_bot_token())