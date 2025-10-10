import asyncio
import logging
from pyrogram import Client
from pyrogram.errors import ChannelPrivate, ChannelInvalid, UsernameNotOccupied
from database import save_message, message_exists
from config import API_ID, API_HASH, SOURCE_CHANNELS

logger = logging.getLogger(__name__)

async def parse_single_channel(client, channel_url):
    """Парсит один канал"""
    try:
        # Извлекаем username из URL
        if channel_url.startswith('https://t.me/'):
            channel_id = channel_url.replace('https://t.me/', '')
        else:
            channel_id = channel_url
        
        logger.info(f"🔍 Парсим: {channel_id}")
        
        # Получаем информацию о канале
        chat = await client.get_chat(channel_id)
        logger.info(f"   📝 Канал: {chat.title}")
        
        # Парсим сообщения
        messages_count = 0
        new_messages_count = 0
        parsed_messages = []
        
        async for message in client.get_chat_history(chat.id, limit=10):
            if message.text and message.text.strip():
                message_text = message.text.strip()
                messages_count += 1
                
                # Проверяем на дубликаты
                if not message_exists(message_text, channel_url):
                    save_message(message_text, channel_url, 'OTHER')
                    parsed_messages.append(message_text)
                    new_messages_count += 1
        
        logger.info(f"   ✅ Найдено {new_messages_count} новых из {messages_count} сообщений")
        
        return {
            'channel': channel_id,
            'title': chat.title,
            'new_messages': new_messages_count,
            'total_messages': messages_count,
            'messages': parsed_messages,
            'success': True
        }
        
    except ChannelPrivate:
        logger.error(f"   ❌ Канал приватный: нет доступа")
        return {'success': False, 'error': 'Private channel'}
    except ChannelInvalid:
        logger.error(f"   ❌ Неверный канал: не существует")
        return {'success': False, 'error': 'Invalid channel'}
    except UsernameNotOccupied:
        logger.error(f"   ❌ Канал не существует")
        return {'success': False, 'error': 'Username not occupied'}
    except Exception as e:
        logger.error(f"   ❌ Ошибка: {str(e)}")
        return {'success': False, 'error': str(e)}

async def parse_all_channels_simple():
    """Парсит все каналы (упрощенная версия)"""
    logger.info("🚀 ЗАПУСК УПРОЩЕННОГО ПАРСЕРА")
    logger.info("=" * 50)
    
    client = None
    try:
        # Используем пользовательскую сессию
        client = Client(
            "telegram_parser",
            api_id=API_ID,
            api_hash=API_HASH,
            workdir="/opt/render/project/src"
        )
        
        await client.start()
        me = await client.get_me()
        logger.info(f"✅ Аутентифицирован как: {me.first_name} (@{me.username})")
        logger.info(f"   Тип: {'Бот' if me.is_bot else 'Пользователь'}")
        
        # Парсим каналы
        all_messages = []
        channel_stats = []
        
        for channel_url in SOURCE_CHANNELS[:3]:  # Парсим только первые 3 для теста
            result = await parse_single_channel(client, channel_url)
            channel_stats.append(result)
            
            if result['success'] and result['messages']:
                all_messages.extend(result['messages'])
        
        logger.info("=" * 50)
        logger.info(f"📊 ВСЕГО НАЙДЕНО: {len(all_messages)} новых сообщений")
        
        return {
            'messages': all_messages,
            'stats': channel_stats,
            'total_messages': len(all_messages)
        }
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        return {'messages': [], 'stats': [], 'total_messages': 0, 'error': str(e)}
    finally:
        if client:
            await client.stop()