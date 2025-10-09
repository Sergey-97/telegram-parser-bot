import asyncio
from pyrogram import Client
from config import API_ID, API_HASH

async def create_test_channel():
    """Создает тестовый канал для публикации"""
    client = Client("telegram_parser", api_id=API_ID, api_hash=API_HASH)
    
    await client.start()
    
    try:
        # Создаем публичный канал
        channel = await client.create_channel(
            title="📊 Тест Аналитика Маркетплейсов",
            description="Канал для тестирования парсера маркетплейсов"
        )
        
        # Делаем канал публичным
        await client.set_chat_username(channel.id, f"test_marketplace_analytics_{channel.id}")
        
        print(f"✅ Создан канал: https://t.me/test_marketplace_analytics_{channel.id}")
        print(f"📝 ID канала: {channel.id}")
        
        return channel.id
        
    except Exception as e:
        print(f"❌ Ошибка создания канала: {e}")
        # Пробуем использовать личные сообщения
        me = await client.get_me()
        print(f"📨 Будем отправлять в 'Сохраненные сообщения'")
        return "me"
    
    finally:
        await client.stop()

async def check_channel_access(client, channel):
    """Проверяет доступ к каналу"""
    try:
        if channel == "me":
            return True
            
        chat = await client.get_chat(channel)
        permissions = await client.get_chat_member(chat.id, "me")
        
        if permissions.can_send_messages:
            print(f"✅ Есть права на отправку в {chat.title}")
            return True
        else:
            print(f"❌ Нет прав на отправку в {chat.title}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка доступа к каналу {channel}: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(create_test_channel())