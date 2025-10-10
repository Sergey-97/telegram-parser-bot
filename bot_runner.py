import asyncio
import logging
from pyrogram import Client
from database import get_last_messages, save_post, save_message, message_exists
from ai_processor import AIProcessor
from post_formatter import PostFormatter
from config import API_ID, API_HASH, TARGET_CHANNEL, BOT_TOKEN, SOURCE_CHANNELS

logger = logging.getLogger(__name__)

async def run_bot():
    """Основная функция запуска бота с реальным парсингом"""
    logger.info("=" * 60)
    logger.info("🚀 ЗАПУСК БОТА - РЕАЛЬНЫЙ ПАРСИНГ")
    logger.info("=" * 60)
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен")
        return "❌ BOT_TOKEN не установлен"
    
    client = None
    try:
        # Аутентификация
        logger.info("1. 🔐 Аутентификация бота...")
        client = Client(
            "telegram_bot", 
            api_id=API_ID, 
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workdir="./"
        )
        
        await client.start()
        me = await client.get_me()
        logger.info(f"✅ Бот аутентифицирован: @{me.username}")
        
        # РЕАЛЬНЫЙ ПАРСИНГ КАНАЛОВ
        logger.info("2. 🔍 ЗАПУСК РЕАЛЬНОГО ПАРСИНГА КАНАЛОВ...")
        all_parsed_messages = await parse_all_channels(client)
        
        # Создание поста
        ai_processor = AIProcessor()
        post_formatter = PostFormatter()
        
        if all_parsed_messages:
            logger.info(f"3. 🧠 СОЗДАНИЕ ПОСТА НА ОСНОВЕ {len(all_parsed_messages)} РЕАЛЬНЫХ СООБЩЕНИЙ")
            structured_content = ai_processor.structure_content(all_parsed_messages, [])
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
        
        # Форматирование и отправка
        post_content = post_formatter.format_structured_post(structured_content)
        save_post(post_content)
        
        # Отправка поста
        logger.info("4. 📤 ОТПРАВКА ПОСТА...")
        max_length = 4096
        if len(post_content) > max_length:
            post_content = post_content[:max_length-100] + "\n\n... (пост сокращен)"
        
        await client.send_message(TARGET_CHANNEL, post_content)
        logger.info(f"✅ ПОСТ УСПЕШНО ОПУБЛИКОВАН В КАНАЛЕ {TARGET_CHANNEL}")
        
        # Итоговая статистика
        result_message = f"✅ Пост отправлен! Реальных сообщений: {len(all_parsed_messages)}"
        logger.info(f"🎯 ИТОГ: {result_message}")
        
        return result_message
        
    except Exception as e:
        logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        logger.error(f"🔍 ДЕТАЛИ ОШИБКИ: {traceback.format_exc()}")
        return f"❌ Ошибка: {str(e)}"
    finally:
        if client:
            await client.stop()

async def parse_all_channels(client):
    """Парсит все каналы и возвращает реальные сообщения"""
    all_messages = []
    total_new_messages = 0
    
    logger.info(f"📡 ПАРСИНГ {len(SOURCE_CHANNELS)} КАНАЛОВ:")
    
    for i, channel_url in enumerate(SOURCE_CHANNELS, 1):
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
            chat = await client.get_chat(channel_id)
            logger.info(f"      📝 Канал: {chat.title}")
            
            # Парсим сообщения
            channel_messages = []
            messages_count = 0
            
            async for message in client.get_chat_history(chat.id, limit=15):
                if message.text and message.text.strip():
                    message_text = message.text.strip()
                    
                    # Проверяем на дубликаты
                    if not message_exists(message_text, channel_url):
                        # Сохраняем в базу
                        save_message(message_text, channel_url, 'OTHER')
                        channel_messages.append(message_text)
                        messages_count += 1
            
            all_messages.extend(channel_messages)
            total_new_messages += messages_count
            
            if messages_count > 0:
                logger.info(f"      ✅ Найдено {messages_count} новых сообщений")
                # Логируем первые 2 сообщения для отладки
                for j, msg in enumerate(channel_messages[:2], 1):
                    logger.info(f"         {j}. {msg[:100]}...")
            else:
                logger.info(f"      ⚠️ Новых сообщений не найдено")
            
        except Exception as e:
            logger.error(f"      ❌ Ошибка парсинга {channel_url}: {str(e)}")
    
    logger.info(f"📊 ВСЕГО НАЙДЕНО: {total_new_messages} новых сообщений из {len(SOURCE_CHANNELS)} каналов")
    return all_messages

def get_fallback_messages():
    """Возвращает тестовые сообщения если парсинг не сработал"""
    return [
        "OZON: новые правила модерации карточек товаров с 1 ноября",
        "Wildberries увеличивает комиссию для категории 'Электроника' с 5% до 7%",
        "Яндекс Маркет запускает экспресс-доставку за 2 часа в Москве",
        "OZON Travel: добавлены новые направления для бронирования отелей",
        "WB вводит обязательную маркировку для товаров категории 'Одежда'",
        "OZON Карта: кешбэк увеличен до 10% для постоянных покупателей",
        "Wildberries обновляет алгоритм выдачи товаров в поиске",
        "Яндекс Доставка расширяет зону покрытия до 200 городов",
        "OZON Marketplace: новые требования к описанию товаров",
        "WB: изменения в политике возвратов - срок увеличен до 45 дней"
    ]