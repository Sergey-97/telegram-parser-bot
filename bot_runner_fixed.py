import asyncio
import logging
from auth_system import auth_system
from pyrogram.errors import ChannelInvalid, ChannelPrivate, UsernameNotOccupied
from database import get_last_messages, save_post, save_message, message_exists
from ai_processor import AIProcessor
from post_formatter import PostFormatter
from config import TARGET_CHANNEL, SOURCE_CHANNELS

logger = logging.getLogger(__name__)

async def run_bot_fixed():
    """Исправленная версия бота с гарантированной пользовательской сессией"""
    logger.info("=" * 60)
    logger.info("🚀 ЗАПУСК - ГАРАНТИРОВАННАЯ ПОЛЬЗОВАТЕЛЬСКАЯ СЕССИЯ")
    logger.info("=" * 60)
    
    try:
        # 1. Получаем пользовательского клиента
        logger.info("1. 🔐 ПОЛУЧЕНИЕ ПОЛЬЗОВАТЕЛЬСКОГО КЛИЕНТА...")
        user_client = await auth_system.get_user_client()
        
        # 2. Парсинг каналов
        logger.info("2. 🔍 ЗАПУСК ПАРСИНГА...")
        parsing_results = await parse_channels_guaranteed(user_client)
        
        all_parsed_messages = parsing_results['messages']
        channel_stats = parsing_results['stats']
        
        # 3. Создание поста
        ai_processor = AIProcessor()
        post_formatter = PostFormatter()
        
        if all_parsed_messages:
            logger.info(f"3. 🧠 СОЗДАНИЕ ПОСТА НА ОСНОВЕ {len(all_parsed_messages)} РЕАЛЬНЫХ СООБЩЕНИЙ")
            structured_content = ai_processor.structure_content(all_parsed_messages, [])
            post_type = "РЕАЛЬНЫЕ ДАННЫЕ"
        else:
            logger.info("3. 🔄 ИСПОЛЬЗУЮ РЕЗЕРВНЫЙ КОНТЕНТ")
            recent_messages = get_last_messages(limit=10)
            if recent_messages:
                texts = [msg['text'] for msg in recent_messages if msg['text']]
                logger.info(f"   📊 Использую {len(texts)} сообщений из базы данных")
            else:
                texts = get_fallback_messages()
                logger.info("   📝 Использую тестовые данные")
            
            structured_content = ai_processor.structure_content(texts, [])
            post_type = "РЕЗЕРВНЫЕ ДАННЫЕ"
        
        post_content = post_formatter.format_structured_post(structured_content)
        save_post(post_content)
        
        # 4. Отправка поста
        logger.info("4. 📤 ОТПРАВКА ПОСТА...")
        bot_client = await auth_system.get_bot_client()
        if bot_client:
            max_length = 4096
            if len(post_content) > max_length:
                post_content = post_content[:max_length-100] + "\n\n... (пост сокращен)"
            
            await bot_client.send_message(TARGET_CHANNEL, post_content)
            logger.info(f"✅ ПОСТ ОПУБЛИКОВАН В {TARGET_CHANNEL}")
        else:
            logger.warning("⚠️ Бот не доступен для отправки")
        
        # 5. Статистика
        stats_message = generate_stats_message(channel_stats, len(all_parsed_messages), post_type)
        logger.info(f"🎯 ИТОГ: {stats_message}")
        
        return f"""
        <h2>🎯 Результат выполнения (ГАРАНТИРОВАННАЯ СЕССИЯ)</h2>
        <p><strong>Тип поста:</strong> {post_type}</p>
        <p><strong>Реальных сообщений:</strong> {len(all_parsed_messages)}</p>
        <h3>📊 Статистика по каналам:</h3>
        <pre>{stats_message}</pre>
        <p><strong>✅ Использована пользовательская сессия для парсинга</strong></p>
        <a href="/">← Назад</a>
        """
        
    except Exception as e:
        logger.error(f"❌ ОШИБКА: {e}")
        import traceback
        logger.error(f"🔍 ДЕТАЛИ: {traceback.format_exc()}")
        return f"❌ Ошибка: {str(e)}"

async def parse_channels_guaranteed(user_client):
    """Гарантированный парсинг с пользовательской сессией"""
    all_messages = []
    channel_stats = {}
    
    logger.info(f"📡 ПАРСИНГ {len(SOURCE_CHANNELS)} КАНАЛОВ:")
    logger.info("=" * 50)
    
    for i, channel_url in enumerate(SOURCE_CHANNELS, 1):
        channel_messages = []
        try:
            # Извлекаем идентификатор канала
            if channel_url.startswith('https://t.me/'):
                channel_id = channel_url.replace('https://t.me/', '')
            elif channel_url.startswith('@'):
                channel_id = channel_url[1:]
            else:
                channel_id = channel_url
            
            logger.info(f"   {i}. 🔍 Парсим: {channel_id}")
            
            # Получаем канал
            chat = await user_client.get_chat(channel_id)
            logger.info(f"      📝 Название: {chat.title}")
            
            # Парсим сообщения (гарантированно работает с пользователем)
            messages_count = 0
            new_messages_count = 0
            
            async for message in user_client.get_chat_history(chat.id, limit=25):
                if message.text and message.text.strip():
                    message_text = message.text.strip()
                    messages_count += 1
                    
                    if not message_exists(message_text, channel_url):
                        save_message(message_text, channel_url, 'OTHER')
                        channel_messages.append(message_text)
                        new_messages_count += 1
            
            all_messages.extend(channel_messages)
            
            channel_stats[channel_id] = {
                'title': chat.title,
                'total_messages': messages_count,
                'new_messages': new_messages_count,
                'success': True
            }
            
            if new_messages_count > 0:
                logger.info(f"      ✅ Найдено {new_messages_count} новых сообщений")
                for j, msg in enumerate(channel_messages[:2], 1):
                    logger.info(f"         📨 {j}. {msg[:80]}...")
            else:
                logger.info(f"      ⚠️ Новых сообщений: 0")
            
        except Exception as e:
            logger.error(f"      ❌ Ошибка: {str(e)}")
            channel_stats[channel_url] = {'success': False, 'error': str(e)}
    
    logger.info("=" * 50)
    logger.info(f"📊 ВСЕГО НАЙДЕНО: {len(all_messages)} новых сообщений")
    
    return {
        'messages': all_messages,
        'stats': channel_stats
    }

def generate_stats_message(channel_stats, total_messages, post_type):
    """Генерирует статистику"""
    stats_lines = []
    stats_lines.append(f"ТИП ПОСТА: {post_type}")
    stats_lines.append(f"ВСЕГО СООБЩЕНИЙ: {total_messages}")
    stats_lines.append("СТАТИСТИКА ПО КАНАЛАМ:")
    stats_lines.append("-" * 40)
    
    successful_channels = 0
    for channel, stats in channel_stats.items():
        if stats.get('success'):
            successful_channels += 1
            stats_lines.append(f"✅ {channel}")
            stats_lines.append(f"   📨 Новых: {stats.get('new_messages', 0)}")
        else:
            stats_lines.append(f"❌ {channel}")
            stats_lines.append(f"   💥 {stats.get('error', 'Unknown')}")
    
    stats_lines.append(f"УСПЕШНЫХ КАНАЛОВ: {successful_channels}/{len(channel_stats)}")
    
    return "\n".join(stats_lines)

def get_fallback_messages():
    """Резервные сообщения"""
    return [
        "OZON: новые правила модерации карточек товаров",
        "Wildberries увеличивает комиссию для электроники",
        "Яндекс Маркет запускает экспресс-доставку",
        "OZON Travel: новые направления",
        "WB вводит обязательную маркировку"
    ]