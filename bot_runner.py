import asyncio
import logging
from pyrogram import Client
from database import get_last_messages, save_post
from parser import TelegramParser
from ai_processor import AIProcessor
from post_formatter import PostFormatter
from config import API_ID, API_HASH, TARGET_CHANNEL

logger = logging.getLogger(__name__)

async def run_bot():
    """Основная функция запуска бота"""
    logger.info("🚀 Запуск Telegram парсера...")
    
    client = Client("telegram_parser", api_id=API_ID, api_hash=API_HASH)
    
    try:
        await client.start()
        logger.info("✅ Успешная аутентификация в Telegram")
        
        # Инициализация компонентов
        parser = TelegramParser(client)
        ai_processor = AIProcessor()
        post_formatter = PostFormatter()
        
        # Парсинг каналов
        logger.info("🔍 Запуск парсинга каналов...")
        parsing_results = await parser.parse_all_channels()
        
        # Создание поста
        if parsing_results['total_new_messages'] >= 3:
            logger.info("🧠 Создание поста на основе новых сообщений...")
            post = await create_post_with_real_parsing(parsing_results, ai_processor, post_formatter)
        else:
            logger.info("🔄 Создание резервного поста...")
            post = await create_fallback_post(ai_processor, post_formatter)
        
        # Сохранение и публикация
        save_post(post)
        await publish_post(client, post)
        
        logger.info("✅ Бот успешно завершил работу")
        
    except Exception as e:
        logger.error(f"❌ Ошибка в работе бота: {e}")
        raise
    finally:
        await safe_stop_client(client)

async def create_post_with_real_parsing(parsing_results, ai_processor, post_formatter):
    """Создает пост на основе реальных данных парсинга"""
    try:
        source_texts = []
        discussion_texts = []
        
        for result in parsing_results['results']:
            if result['new_messages'] > 0:
                messages = result.get('messages', [])
                for msg in messages:
                    if result['type'] == 'main':
                        source_texts.append(msg)
                    else:
                        discussion_texts.append(msg)
        
        logger.info(f"📊 Обработка {len(source_texts)} основных и {len(discussion_texts)} дискуссионных сообщений")
        
        structured_content = ai_processor.structure_content(source_texts, discussion_texts)
        post_content = post_formatter.format_structured_post(structured_content)
        
        return post_content
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания поста: {e}")
        return await create_fallback_post(ai_processor, post_formatter)

async def create_fallback_post(ai_processor, post_formatter):
    """Создает резервный пост"""
    recent_messages = get_last_messages(limit=10)
    
    if recent_messages:
        texts = [msg['text'] for msg in recent_messages if msg['text']]
        structured_content = ai_processor.structure_content(texts, [])
    else:
        structured_content = {
            'title': '📊 Еженедельный обзор маркетплейсов',
            'summary': 'Анализ ключевых изменений и трендов на основных маркетплейсах',
            'sections': {
                'OZON': {
                    'key_points': [
                        'Обновления платформы для продавцов',
                        'Изменения в логистических процессах',
                        'Новые маркетинговые инструменты'
                    ],
                    'important': ['Рекомендуется проверить настройки личного кабинета'],
                    'tips': ['Используйте все доступные инструменты аналитики']
                },
                'WB': {
                    'key_points': [
                        'Оптимизация процессов выкупа',
                        'Обновления в работе с возвратами',
                        'Изменения в алгоритмах выдачи'
                    ],
                    'important': ['Внимание к изменениям в регламентах'],
                    'tips': ['Регулярно мониторьте статистику продаж']
                }
            },
            'recommendations': 'Следите за официальными объявлениями маркетплейсов и участвуйте в профессиональных сообществах'
        }
    
    return post_formatter.format_structured_post(structured_content)

async def publish_post(client, post_content):
    """Публикует пост в целевой канал"""
    try:
        # Ограничиваем длину поста для Telegram
        max_length = 4096
        if len(post_content) > max_length:
            post_content = post_content[:max_length-100] + "\n\n... (пост сокращен)"
        
        await client.send_message(TARGET_CHANNEL, post_content)
        logger.info(f"✅ Пост успешно опубликован в канале {TARGET_CHANNEL}")
        
        # Дублируем в логи для отладки
        logger.info(f"📝 Содержание поста:\n{post_content[:500]}...")
        
    except Exception as e:
        logger.error(f"❌ Ошибка публикации поста: {e}")
        # Пробуем отправить в сохраненные сообщения для отладки
        try:
            await client.send_message("me", "❌ Не удалось отправить в канал. Ошибка: " + str(e))
        except:
            pass
        raise

async def safe_stop_client(client):
    """Безопасная остановка клиента"""
    try:
        if client.is_connected:
            await client.stop()
    except Exception as e:
        logger.warning(f"⚠️ Ошибка при остановке клиента: {e}")