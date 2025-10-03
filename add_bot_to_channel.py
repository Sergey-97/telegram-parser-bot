import asyncio
from telethon import TelegramClient
from dotenv import load_dotenv
import os

# Загружаем переменные из .env файла
load_dotenv()

async def add_bot_as_admin():
    """
    Добавляем бота в канал как администратора используя ваш аккаунт
    """
    print("=" * 50)
    print("🚀 ДОБАВЛЕНИЕ БОТА В КАНАЛ")
    print("=" * 50)
    
    # Создаем клиент с вашим ЛИЧНЫМ аккаунтом
    client = TelegramClient(
        'user_session', 
        int(os.getenv('API_ID')), 
        os.getenv('API_HASH')
    )
    
    print("🔑 ШАГ 1: Авторизация в вашем аккаунте")
    print("Нужно ввести ваш номер телефона и код подтверждения")
    print("-" * 40)
    
    # Запускаем авторизацию
    await client.start()
    
    try:
        print("\n✅ Авторизация успешна!")
        me = await client.get_me()
        print(f"👤 Вы вошли как: {me.first_name}")
        
        print("\n🔍 ШАГ 2: Поиск канала @mar_factor...")
        # Получаем канал
        channel = await client.get_entity('https://t.me/mar_factor')
        print(f"✅ Канал найден: {channel.title}")
        
        print("\n🔍 ШАГ 3: Поиск бота @marketfactor_bot...")
        # Получаем бота
        bot = await client.get_entity('@marketfactor_bot')
        print(f"✅ Бот найден: {bot.first_name} (@{bot.username})")
        
        print("\n👨‍💼 ШАГ 4: Добавление бота как администратора...")
        print("Настраиваем права...")
        
        # ✅ ИСПРАВЛЕННЫЙ ВАРИАНТ - правильные параметры
        await client.edit_admin(
            entity=channel,  # ✅ ПРАВИЛЬНЫЙ параметр вместо 'channel'
            user=bot,
            is_admin=True,
            # ВКЛЮЧАЕМ только необходимые права:
            post_messages=True,      # ✅ Может публиковать сообщения
            edit_messages=True,      # ✅ Может редактировать сообщения
            # ОСТАЛЬНЫЕ права ВЫКЛЮЧАЕМ:
            delete_messages=False,
            ban_users=False,
            invite_users=False,
            pin_messages=False,
            add_admins=False,
            change_info=False
        )
        
        print("\n" + "=" * 50)
        print("🎉 УСПЕХ! БОТ ДОБАВЛЕН КАК АДМИНИСТРАТОР!")
        print("=" * 50)
        print("✅ Бот @marketfactor_bot теперь может:")
        print("   📝 Публиковать сообщения в @mar_factor")
        print("   ✏️ Редактировать сообщения")
        print("")
        print("🔧 Следующий шаг: запустите test_bot_simple.py для проверки")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        print("\n🔧 Возможные решения:")
        print("1. Убедитесь, что вы владелец/администратор канала")
        print("2. Проверьте, что бот не забанен в канале")
        print("3. Попробуйте добавить бота через веб-версию Telegram")
    
    finally:
        await client.disconnect()
        print("\n🔚 Сессия завершена")

# Запускаем функцию
if __name__ == "__main__":
    print("Подготовка к добавлению бота...")
    asyncio.run(add_bot_as_admin())