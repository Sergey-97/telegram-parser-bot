import asyncio
import os
import sys
from datetime import datetime
from pyrogram import Client
from database import init_db, get_last_messages, save_post
from parser import TelegramParser
from ai_processor import AIProcessor
from post_formatter import PostFormatter
from config import API_ID, API_HASH

async def main():
    """Основная асинхронная функция"""
    print("=" * 60)
    print("🚀 TELEGRAM AI ПАРСЕР БОТ - РЕАЛЬНЫЙ ПАРСИНГ")
    print("=" * 60)
    
    # Инициализируем компоненты
    client = Client("telegram_parser", api_id=API_ID, api_hash=API_HASH)
    parser = TelegramParser(client)
    ai_processor = AIProcessor()
    post_formatter = PostFormatter()
    
    try:
        # Запускаем клиента
        await client.start()
        print("✅ Успешная аутентификация")
        
        # Запускаем парсинг
        print("🔍 Запускаю реальный парсинг каналов...")
        parsing_results = await parser.parse_all_channels()
        
        # Создаем пост на основе результатов
        if parsing_results['total_new_messages'] >= 3:
            print("🧠 Обрабатываю реальный контент...")
            post = await create_post_with_real_parsing(parsing_results, ai_processor, post_formatter)
        else:
            print("⚠️  Мало данных от парсинга, использую резервный контент")
            post = await create_fallback_post(ai_processor, post_formatter)
        
        # Сохраняем пост в базу
        save_post(post)
        
        # Отправляем пост
        await send_post(client, post)
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Безопасная остановка
        await safe_stop_client(client)

async def safe_stop_client(client):
    """Безопасная остановка клиента"""
    try:
        if client.is_connected:
            await client.stop()
            print("✅ Pyrogram клиент остановлен")
    except Exception as e:
        print(f"⚠️  Ошибка при остановке клиента: {e}")

async def create_post_with_real_parsing(parsing_results, ai_processor, post_formatter):
    """Создает пост на основе реальных данных парсинга"""
    try:
        # Получаем тексты сообщений для AI обработки
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
        
        print(f"📥 РЕЗУЛЬТАТЫ ПАРСИНГА:")
        print(f"   Основные каналы: {len(source_texts)} сообщений")
        print(f"   Обсуждения: {len(discussion_texts)} сообщений")
        
        # Структурируем контент через AI
        structured_content = ai_processor.structure_content(source_texts, discussion_texts)
        
        # Форматируем пост
        post_content = post_formatter.format_structured_post(structured_content)
        
        return post_content
        
    except Exception as e:
        print(f"❌ Ошибка создания поста: {e}")
        return await create_fallback_post(ai_processor, post_formatter)

async def create_fallback_post(ai_processor, post_formatter):
    """Создает резервный пост при недостатке данных"""
    print("🔄 Создаю резервный пост...")
    
    # Используем последние сообщения из базы данных
    recent_messages = get_last_messages(limit=10)
    
    if recent_messages:
        texts = [msg['text'] for msg in recent_messages if msg['text']]
        structured_content = ai_processor.structure_content(texts, [])
    else:
        # Полностью резервный контент
        structured_content = {
            'title': '📊 Аналитика маркетплейсов',
            'summary': 'Ежедневный обзор ключевых трендов и изменений',
            'sections': {
                'OZON': {
                    'key_points': [
                        'Обновления платформы для продавцов',
                        'Изменения в логистических процессах'
                    ],
                    'important': ['Рекомендуется проверить настройки личного кабинета'],
                    'tips': ['Используйте все доступные инструменты аналитики']
                },
                'WB': {
                    'key_points': [
                        'Оптимизация процессов выкупа',
                        'Обновления в работе с возвратами'
                    ],
                    'important': ['Внимание к изменениям в регламентах'],
                    'tips': ['Регулярно мониторьте статистику продаж']
                }
            },
            'recommendations': 'Следите за официальными объявлениями маркетплейсов'
        }
    
    post_content = post_formatter.format_structured_post(structured_content)
    return post_content

async def send_post(client, post_content):
    """Отправляет пост в сохраненные сообщения"""
    try:
        # Разбиваем длинные посты на части
        max_length = 4096
        if len(post_content) > max_length:
            post_content = post_content[:max_length-100] + "\n\n... (пост сокращен)"
        
        await client.send_message("me", post_content)
        print("✅ Пост успешно отправлен в 'Сохраненные сообщения'!")
        print("=" * 40)
        print("📝 СОДЕРЖАНИЕ ПОСТА:")
        print("=" * 40)
        print(post_content)
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ Ошибка отправки поста: {e}")

if __name__ == "__main__":
    # Запускаем бота
    asyncio.run(main())
    print("✅ Работа завершена")