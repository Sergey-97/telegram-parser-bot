import asyncio
import logging
from advanced_parser import parse_all_channels_advanced
from telegram_manager import telegram_manager
from ai_processor import AIProcessor
from post_formatter import PostFormatter
from database import get_last_messages, save_post
from parsing_state import is_first_run, get_parsing_stats

logger = logging.getLogger(__name__)

async def run_advanced_bot():
    """Улучшенная версия бота с умным парсингом"""
    logger.info("=" * 60)
    logger.info("🚀 ЗАПУСК УЛУЧШЕННОГО ПАРСЕРА")
    logger.info("=" * 60)
    
    # Проверяем, первый ли это запуск
    first_run = is_first_run()
    if first_run:
        logger.info("🎯 РЕЖИМ: ПЕРВЫЙ ЗАПУСК - парсим по 10 сообщений с каждого канала")
    else:
        logger.info("🎯 РЕЖИМ: РЕГУЛЯРНЫЙ ПАРСИНГ - ищем только новые сообщения")
    
    try:
        # 1. Парсинг каналов
        logger.info("1. 🔍 УМНЫЙ ПАРСИНГ КАНАЛОВ...")
        parsing_results = await parse_all_channels_advanced()
        
        all_messages = parsing_results['messages']
        channel_stats = parsing_results['stats']
        total_new_messages = parsing_results['total_new_messages']
        
        # 2. Создание поста
        logger.info("2. 🧠 АНАЛИЗ И СОЗДАНИЕ ПОСТА...")
        ai_processor = AIProcessor()
        post_formatter = PostFormatter()
        
        if all_messages:
            logger.info(f"   📊 Использую {len(all_messages)} сообщений для анализа")
            structured_content = ai_processor.structure_content(all_messages, [])
            post_type = "РЕАЛЬНЫЕ ДАННЫЕ"
            data_source = f"на основе {total_new_messages} новых сообщений"
        else:
            logger.info("   🔄 Использую резервный контент")
            recent_messages = get_last_messages(limit=10)
            if recent_messages:
                texts = [msg['text'] for msg in recent_messages if msg['text']]
                logger.info(f"   📁 Из базы: {len(texts)} сообщений")
                data_source = "на основе данных из базы"
            else:
                texts = get_fallback_messages()
                logger.info("   📝 Тестовые данные")
                data_source = "тестовые данные"
            
            structured_content = ai_processor.structure_content(texts, [])
            post_type = "РЕЗЕРВНЫЕ ДАННЫЕ"
        
        post_content = post_formatter.format_structured_post(structured_content)
        save_post(post_content)
        
        # 3. Отправка поста
        logger.info("3. 📤 ОТПРАВКА ПОСТА...")
        send_success = await telegram_manager.send_message(post_content)
        
        # 4. Детальная статистика
        stats = get_parsing_stats()
        stats_text = generate_detailed_stats(
            channel_stats, 
            total_new_messages, 
            len(all_messages),
            post_type, 
            send_success,
            stats,
            first_run
        )
        
        logger.info(f"🎯 ИТОГ: {stats_text}")
        
        return create_result_html(
            post_type, 
            total_new_messages, 
            len(all_messages),
            send_success, 
            stats_text, 
            post_content,
            data_source,
            first_run
        )
        
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")
        import traceback
        logger.error(f"🔍 Детали: {traceback.format_exc()}")
        return f"❌ Ошибка: {str(e)}"

def generate_detailed_stats(channel_stats, new_messages, total_messages, post_type, send_success, parsing_stats, first_run):
    """Генерирует детальную статистику"""
    lines = []
    lines.append(f"🎯 РЕЖИМ: {'ПЕРВЫЙ ЗАПУСК' if first_run else 'РЕГУЛЯРНЫЙ ПАРСИНГ'}")
    lines.append(f"📊 ТИП ПОСТА: {post_type}")
    lines.append(f"📨 НОВЫХ СООБЩЕНИЙ: {new_messages}")
    lines.append(f"📝 ВСЕГО СООБЩЕНИЙ: {total_messages}")
    lines.append(f"📤 ОТПРАВКА: {'✅ УСПЕШНО' if send_success else '❌ НЕ УДАЛОСЬ'}")
    lines.append("")
    
    lines.append("📡 СТАТИСТИКА ПАРСИНГА:")
    lines.append("-" * 50)
    
    successful_parses = 0
    for stat in channel_stats:
        if stat.get('success'):
            successful_parses += 1
            mode = "🆕 ПЕРВЫЙ" if stat.get('is_first_run') else "🔄 ОБНОВЛЕНИЕ"
            lines.append(f"✅ {stat['channel']} ({mode})")
            lines.append(f"   📝 {stat['title']}")
            lines.append(f"   📨 Новых: {stat['new_messages']}")
            lines.append(f"   📊 Обработано: {stat['total_processed']}")
        else:
            lines.append(f"❌ {stat.get('channel', 'N/A')}")
            lines.append(f"   💥 {stat.get('error', 'Unknown error')}")
        lines.append("")
    
    lines.append(f"✅ УСПЕШНЫХ ПАРСИНГОВ: {successful_parses}/{len(channel_stats)}")
    lines.append(f"📈 ВСЕГО СООБЩЕНИЙ В БАЗЕ: {parsing_stats['total_messages_parsed']}")
    lines.append(f"🌐 ОБРАБОТАНО КАНАЛОВ: {parsing_stats['total_channels']}")
    
    return "\n".join(lines)

def create_result_html(post_type, new_messages, total_messages, send_success, stats_text, post_content, data_source, first_run):
    """Создает HTML результат"""
    return f"""
    <h2>🎯 Результат выполнения {'(ПЕРВЫЙ ЗАПУСК)' if first_run else '(РЕГУЛЯРНЫЙ ПАРСИНГ)'}</h2>
    
    <div style="background: #f0f8ff; padding: 15px; border-radius: 10px; margin: 10px 0;">
        <p><strong>📊 Тип поста:</strong> {post_type}</p>
        <p><strong>📨 Новых сообщений:</strong> {new_messages}</p>
        <p><strong>📝 Всего сообщений:</strong> {total_messages}</p>
        <p><strong>📤 Отправка:</strong> {'✅ Успешно' if send_success else '❌ Не удалось'}</p>
        <p><strong>📁 Источник данных:</strong> {data_source}</p>
    </div>
    
    <h3>📈 Детальная статистика:</h3>
    <pre style="background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto;">{stats_text}</pre>
    
    <h3>📝 Содержание поста:</h3>
    <pre style="background: #fffacd; padding: 15px; border-radius: 5px; max-height: 300px; overflow-y: auto;">{post_content}</pre>
    
    <p><strong>📋 Подробные логи доступны в Render Dashboard</strong></p>
    <a href="/">← Назад к главной</a>
    """

def get_fallback_messages():
    """Резервные сообщения"""
    return [
        "OZON: обновление правил модерации карточек товаров",
        "Wildberries: изменения в комиссиях для категории электроники",
        "Яндекс Маркет: запуск сервиса экспресс-доставки",
        "OZON Travel: расширение географии бронирования отелей",
        "WB: новые требования к маркировке товаров категории одежда",
        "OZON Карта: увеличение кешбэка для постоянных клиентов",
        "Wildberries: обновление алгоритмов поисковой выдачи",
        "Яндекс Доставка: расширение зоны покрытия службы доставки"
    ]