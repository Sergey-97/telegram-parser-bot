import asyncio
import os
import sys
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import ChannelParticipantsAdmins

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(__file__))

# Загружаем переменные окружения ДО импорта config
load_dotenv()

import config

async def check_bot_status():
    """
    Проверяем, добавлен ли бот в канал и может ли он отправлять сообщения
    """
    # Проверяем, что переменные загружены
    if not config.API_ID or not config.API_HASH:
        print("❌ API_ID или API_HASH не установлены в config.py")
        print("Проверьте файл .env и перезапустите тест")
        return
    
    print(f"🔧 Используем API_ID: {config.API_ID}")
    print(f"🔧 Используем API_HASH: {config.API_HASH[:10]}...")
    
    client = TelegramClient(
        'session_name',
        config.API_ID, 
        config.API_HASH
    )
    
    await client.start(bot_token=config.BOT_TOKEN)
    
    try:
        # 1. Проверяем подключение
        me = await client.get_me()
        print(f"✅ Бот авторизован как: {me.first_name} (@{me.username})")
        
        # 2. Пробуем найти канал mar_factor
        try:
            channel = await client.get_entity(config.TARGET_CHANNEL)
            print(f"✅ Канал найден: {channel.title}")
        except Exception as e:
            print(f"❌ Не удалось найти канал: {e}")
            return
        
        # 3. Проверяем список администраторов
        print("\n📋 Проверяем администраторов канала:")
        admins = await client.get_participants(channel, filter=ChannelParticipantsAdmins)
        
        bot_found = False
        for admin in admins:
            bot_status = "🤖 БОТ" if admin.bot else "👤 Человек"
            print(f"   {bot_status}: {admin.first_name} (@{admin.username})")
            if admin.bot:
                bot_found = True
        
        if not bot_found:
            print("❌ Бот не найден среди администраторов!")
        else:
            print("✅ Бот найден среди администраторов!")
        
        # 4. Пробуем отправить тестовое сообщение
        print("\n📤 Пробуем отправить тестовое сообщение...")
        try:
            message = await client.send_message(
                channel, 
                "🤖 Тестовое сообщение от бота\n" +
                "Если вы это видите - бот работает корректно!"
            )
            print("✅ Сообщение успешно отправлено!")
            
            # Удаляем тестовое сообщение
            await asyncio.sleep(3)
            await message.delete()
            print("✅ Тестовое сообщение удалено")
            
        except Exception as e:
            print(f"❌ Ошибка при отправке сообщения: {e}")
            print("\nВозможные причины:")
            print("1. Бот не добавлен как администратор")
            print("2. У бота нет прав на отправку сообщений")
            print("3. Канал закрытый и нужны дополнительные права")
    
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
    
    finally:
        await client.disconnect()

# Запускаем проверку
if __name__ == "__main__":
    print("🔍 Запускаем проверку бота...")
    asyncio.run(check_bot_status())