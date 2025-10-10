import os
import asyncio
import sys
from pyrogram import Client
from config import API_ID, API_HASH

async def force_create_session():
    """Принудительно создает пользовательскую сессию на Render"""
    print("🔐 ПРИНУДИТЕЛЬНОЕ СОЗДАНИЕ ПОЛЬЗОВАТЕЛЬСКОЙ СЕССИИ НА RENDER")
    print("=" * 60)
    
    # Удаляем старые сессии если есть
    if os.path.exists("telegram_parser.session"):
        os.remove("telegram_parser.session")
        print("🗑️ Удалена старая сессия")
    
    client = Client(
        "telegram_parser",
        api_id=API_ID,
        api_hash=API_HASH,
        workdir="/opt/render/project/src"
    )
    
    try:
        print("📱 Запуск аутентификации...")
        await client.start()
        
        me = await client.get_me()
        print(f"✅ ПОЛЬЗОВАТЕЛЬ АУТЕНТИФИЦИРОВАН: {me.first_name} (@{me.username})")
        print(f"   ID: {me.id}")
        print(f"   Бот: {me.is_bot}")
        
        # Проверяем создание файла
        if os.path.exists("telegram_parser.session"):
            print("✅ Файл telegram_parser.session создан")
            file_size = os.path.getsize("telegram_parser.session")
            print(f"   Размер файла: {file_size} байт")
        else:
            print("❌ Файл сессии не создан!")
            
        await client.stop()
        print("✅ Сессия сохранена")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(force_create_session())