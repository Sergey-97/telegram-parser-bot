import asyncio
import logging
from pyrogram import Client
from pyrogram.errors import ChannelPrivate, ChannelInvalid, UsernameNotOccupied
from database import save_message, message_exists
from parsing_state import get_channel_state, update_channel_state, get_parsing_stats
from config import API_ID, API_HASH, SOURCE_CHANNELS

logger = logging.getLogger(__name__)

async def parse_channel_advanced(client, channel_url, initial_limit=10, regular_limit=20):
    """Продвинутый парсинг канала с отслеживанием состояния"""
    try:
        # Извлекаем username из URL
        if channel_url.startswith('https://t.me/'):
            channel_id = channel_url.replace('https://t.me/', '')
        else:
            channel_id = channel_url
        
        logger.info(f"🔍 Парсим: {channel_id}")
        
        # Получаем состояние канала
        channel_state = get_channel_state(channel_url)
        is_first_run = channel_state['is_first_run']
        
        # Получаем информацию о канале
        chat = await client.get_chat(channel_id)
        logger.info(f"   📝 Канал: {chat.title}")
        logger.info(f"   🎯 Режим: {'ПЕРВЫЙ ЗАПУСК' if is_first_run else 'РЕГУЛЯРНЫЙ ПАРСИНГ'}")
        
        # Определяем лимит сообщений
        message_limit = initial_limit if is_first_run else regular_limit
        logger.info(f"   📨 Лимит: {message_limit} сообщений")
        
        # Парсим сообщения
        messages_count = 0
        new_messages_count = 0
        parsed_messages = []
        last_message_id = 0
        
        async for message in client.get_chat_history(chat.id, limit=message_limit):
            if message.text and message.text.strip():
                message_text = message.text.strip()
                messages_count += 1
                
                # Сохраняем ID последнего сообщения
                if last_message_id == 0:
                    last_message_id = message.id
                
                # Проверяем на дубликаты
                if not message_exists(message_text, channel_url):
                    save_message(message_text, channel_url, 'OTHER')
                    parsed_messages.append(message_text)
                    new_messages_count += 1
        
        # Обновляем состояние парсинга
        if last_message_id > 0:
            update_channel_state(channel_url, last_message_id, new_messages_count)
        
        logger.info(f"   ✅ Обработано: {messages_count} сообщений")
        logger.info(f"   🆕 Новых: {new_messages_count} сообщений")
        
        # Логируем примеры новых сообщений
        if new_messages_count > 0:
            for i, msg in enumerate(parsed_messages[:2], 1):
                logger.info(f"      📨 {i}. {msg[:80]}...")
        
        return {
            'channel': channel_id,
            'title': chat.title,
            'is_first_run': is_first_run,
            'new_messages': new_messages_count,
            'total_processed': messages_count,
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

async def parse_all_channels_advanced():
    """Продвинутый парсинг всех каналов с умной логикой"""
    logger.info("🚀 ЗАПУСК ПРОДВИНУТОГО ПАРСЕРА")
    logger.info("=" * 60)
    
    # Получаем общую статистику
    stats = get_parsing_stats()
    logger.info(f"📊 ОБЩАЯ СТАТИСТИКА: {stats['total_channels']} каналов, {stats['total_messages_parsed']} сообщений")
    
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
        logger.info(f"✅ Аутентифицирован как: {me.first_name}")
        logger.info(f"   Тип: {'🤖 Бот' if me.is_bot else '👤 Пользователь'}")
        
        # Парсим каналы
        all_messages = []
        channel_stats = []
        total_new_messages = 0
        
        for channel_url in SOURCE_CHANNELS:
            result = await parse_channel_advanced(client, channel_url)
            channel_stats.append(result)
            
            if result['success'] and result['messages']:
                all_messages.extend(result['messages'])
                total_new_messages += result['new_messages']
        
        # Итоговая статистика
        logger.info("=" * 60)
        logger.info(f"📊 ИТОГ ПАРСИНГА:")
        logger.info(f"   🆕 Новых сообщений: {total_new_messages}")
        logger.info(f"   📨 Всего сообщений: {len(all_messages)}")
        logger.info(f"   📡 Обработано каналов: {len(channel_stats)}")
        
        successful_parses = sum(1 for stat in channel_stats if stat['success'])
        logger.info(f"   ✅ Успешных парсингов: {successful_parses}/{len(channel_stats)}")
        
        return {
            'messages': all_messages,
            'stats': channel_stats,
            'total_new_messages': total_new_messages,
            'total_messages': len(all_messages),
            'successful_channels': successful_parses,
            'total_channels': len(channel_stats)
        }
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        return {
            'messages': [], 
            'stats': [], 
            'total_new_messages': 0,
            'total_messages': 0,
            'successful_channels': 0,
            'total_channels': 0,
            'error': str(e)
        }
    finally:
        if client:
            await client.stop()