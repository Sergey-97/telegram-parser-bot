import asyncio
import logging
from pyrogram import Client
from pyrogram.errors import ChannelInvalid, ChannelPrivate, UsernameNotOccupied
from database import get_last_messages, save_post, save_message, message_exists
from ai_processor import AIProcessor
from post_formatter import PostFormatter
from config import API_ID, API_HASH, TARGET_CHANNEL, BOT_TOKEN, SOURCE_CHANNELS

logger = logging.getLogger(__name__)

async def run_bot():
    """Основная функция запуска бота с пользовательской сессией"""
    logger.info("=" * 60)
    logger.info("🚀 ЗАПУСК БОТА - ПОЛЬЗОВАТЕЛЬСКАЯ СЕССИЯ")
    logger.info("=" * 60)
    
    # Используем пользовательскую сессию для парсинга
    user_client = None
    bot_client = None
    
    try:
        # 1. Парсинг с пользовательской сессией (telegram_parser.session)
        logger.info("1. 🔐 ПОДКЛЮЧЕНИЕ ПОЛЬЗОВАТЕЛЬСКОЙ СЕССИИ...")
        user_client = Client(
            "telegram_parser",  # Используем существующую сессию
            api_id=API_ID, 
            api_hash=API_HASH,
            workdir="./"
        )
        
        await user_client.start()
        me = await user_client.get_me()
        logger.info(f"✅ Пользователь аутентифицирован: {me.first_name} (@{me.username})")
        
        # 2. Парсинг каналов
        logger.info("2. 🔍 ЗАПУСК ПАРСИНГА КАНАЛОВ...")
        parsing_results = await parse_channels_with_user(user_client)
        
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
        
        # 4. Отправка поста с ботом (если есть токен)
        logger.info("4. 🤖 ОТПРАВКА ПОСТА...")
        if BOT_TOKEN:
            bot_client = Client(
                "telegram_bot",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=BOT_TOKEN,
                workdir="./"
            )
            await bot_client.start()
            
            max_length = 4096
            if len(post_content) > max_length:
                post_content = post_content[:max_length-100] + "\n\n... (пост сокращен)"
            
            await bot_client.send_message(TARGET_CHANNEL, post_content)
            logger.info(f"✅ ПОСТ УСПЕШНО ОПУБЛИКОВАН В КАНАЛЕ {TARGET_CHANNEL}")
        else:
            logger.warning("⚠️ BOT_TOKEN не установлен - пост не отправлен")
        
        # 5. Статистика
        stats_message = generate_stats_message(channel_stats, len(all_parsed_messages), post_type)
        logger.info(f"🎯 ИТОГ: {stats_message}")
        
        return f"""
        <h2>🎯 Результат выполнения</h2>
        <p><strong>Тип поста:</strong> {post_type}</p>
        <p><strong>Реальных сообщений:</strong> {len(all_parsed_messages)}</p>
        <h3>📊 Статистика по каналам:</h3>
        <pre>{stats_message}</pre>
        <p><strong>📋 Подробные логи смотрите в Render Dashboard</strong></p>
        <a href="/">← Назад</a>
        """
        
    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        logger.error(f"🔍 ДЕТАЛИ ОШИБКИ: {traceback.format_exc()}")
        return f"❌ Ошибка: {str(e)}"
    finally:
        if user_client:
            await user_client.stop()
        if bot_client:
            await bot_client.stop()

async def parse_channels_with_user(user_client):
    """Парсинг каналов с пользовательской сессией"""
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
            
            # Получаем информацию о канале
            chat = await user_client.get_chat(channel_id)
            logger.info(f"      📝 Название: {chat.title}")
            
            # Парсим сообщения (теперь это работает с пользовательской сессией!)
            messages_count = 0
            new_messages_count = 0
            
            async for message in user_client.get_chat_history(chat.id, limit=20):
                if message.text and message.text.strip():
                    message_text = message.text.strip()
                    messages_count += 1
                    
                    # Проверяем на дубликаты
                    if not message_exists(message_text, channel_url):
                        # Сохраняем в базу
                        save_message(message_text, channel_url, 'OTHER')
                        channel_messages.append(message_text)
                        new_messages_count += 1
            
            all_messages.extend(channel_messages)
            
            # Статистика по каналу
            channel_stats[channel_id] = {
                'title': chat.title,
                'total_messages': messages_count,
                'new_messages': new_messages_count,
                'success': True
            }
            
            if new_messages_count > 0:
                logger.info(f"      ✅ Найдено {new_messages_count} новых из {messages_count} сообщений")
                # Логируем примеры сообщений
                for j, msg in enumerate(channel_messages[:2], 1):
                    logger.info(f"         📨 {j}. {msg[:80]}...")
            else:
                logger.info(f"      ⚠️ Новых сообщений: 0 (всего сообщений: {messages_count})")
            
        except ChannelPrivate:
            logger.error(f"      ❌ КАНАЛ ПРИВАТНЫЙ: нет доступа")
            channel_stats[channel_url] = {'success': False, 'error': 'Private channel'}
        except ChannelInvalid:
            logger.error(f"      ❌ НЕВЕРНЫЙ КАНАЛ: не существует или недоступен")
            channel_stats[channel_url] = {'success': False, 'error': 'Invalid channel'}
        except UsernameNotOccupied:
            logger.error(f"      ❌ КАНАЛ НЕ СУЩЕСТВУЕТ: username не занят")
            channel_stats[channel_url] = {'success': False, 'error': 'Username not occupied'}
        except Exception as e:
            logger.error(f"      ❌ ОШИБКА ПАРСИНГА: {str(e)}")
            channel_stats[channel_url] = {'success': False, 'error': str(e)}
    
    logger.info("=" * 50)
    logger.info(f"📊 ВСЕГО НАЙДЕНО: {len(all_messages)} новых сообщений")
    
    return {
        'messages': all_messages,
        'stats': channel_stats
    }

def generate_stats_message(channel_stats, total_messages, post_type):
    """Генерирует детальную статистику"""
    stats_lines = []
    stats_lines.append(f"ТИП ПОСТА: {post_type}")
    stats_lines.append(f"ВСЕГО СООБЩЕНИЙ: {total_messages}")
    stats_lines.append("")
    stats_lines.append("СТАТИСТИКА ПО КАНАЛАМ:")
    stats_lines.append("-" * 40)
    
    successful_channels = 0
    for channel, stats in channel_stats.items():
        if stats.get('success'):
            successful_channels += 1
            stats_lines.append(f"✅ {channel}")
            stats_lines.append(f"   📝 {stats.get('title', 'N/A')}")
            stats_lines.append(f"   📨 Новых: {stats.get('new_messages', 0)}")
            stats_lines.append(f"   📊 Всего: {stats.get('total_messages', 0)}")
        else:
            stats_lines.append(f"❌ {channel}")
            stats_lines.append(f"   💥 Ошибка: {stats.get('error', 'Unknown error')}")
        stats_lines.append("")
    
    stats_lines.append(f"УСПЕШНЫХ КАНАЛОВ: {successful_channels}/{len(channel_stats)}")
    
    return "\n".join(stats_lines)

def get_fallback_messages():
    """Возвращает тестовые сообщения если парсинг не сработал"""
    return [
        "OZON: новые правила модерации карточек товаров с 1 ноября - обязательные видеообзоры",
        "Wildberries увеличивает комиссию для категории 'Электроника' с 5% до 7% с 15 ноября",
        "Яндекс Маркет запускает экспресс-доставку за 2 часа в Москве и Санкт-Петербурге",
        "OZON Travel: добавлены новые направления для бронирования отелей в Турции и ОАЭ",
        "WB вводит обязательную маркировку для всех товаров категории 'Одежда'",
        "OZON Карта: кешбэк увеличен до 10% для постоянных покупателей",
        "Wildberries обновляет алгоритм выдачи товаров - приоритет продавцам с высоким рейтингом",
        "Яндекс Доставка расширяет зону покрытия до 200 городов России",
        "OZON Marketplace: новые требования к описанию товаров - минимально 1000 символов",
        "WB: изменения в политике возвратов - срок возврата увеличен до 45 дней"
    ]