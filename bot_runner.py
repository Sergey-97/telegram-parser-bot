import asyncio
import logging
from simple_parser import parse_all_channels_simple
from telegram_manager import telegram_manager
from ai_processor import AIProcessor
from post_formatter import PostFormatter
from database import get_last_messages, save_post

logger = logging.getLogger(__name__)

async def run_bot():
    """Основная функция запуска бота"""
    logger.info("=" * 60)
    logger.info("🚀 ЗАПУСК TELEGRAM ПАРСЕРА")
    logger.info("=" * 60)
    
    try:
        # 1. Парсинг каналов
        logger.info("1. 🔍 ПАРСИНГ КАНАЛОВ...")
        parsing_results = await parse_all_channels_simple()
        
        all_messages = parsing_results['messages']
        channel_stats = parsing_results['stats']
        
        # 2. Создание поста
        logger.info("2. 🧠 СОЗДАНИЕ ПОСТА...")
        ai_processor = AIProcessor()
        post_formatter = PostFormatter()
        
        if all_messages:
            logger.info(f"   📊 Использую {len(all_messages)} реальных сообщений")
            structured_content = ai_processor.structure_content(all_messages, [])
            post_type = "РЕАЛЬНЫЕ ДАННЫЕ"
        else:
            logger.info("   🔄 Использую резервный контент")
            recent_messages = get_last_messages(limit=8)
            if recent_messages:
                texts = [msg['text'] for msg in recent_messages if msg['text']]
                logger.info(f"   📁 Из базы: {len(texts)} сообщений")
            else:
                texts = [
                    "OZON: новые правила модерации карточек товаров",
                    "Wildberries увеличивает комиссию для электроники",
                    "Яндекс Маркет запускает экспресс-доставку",
                    "OZON Travel: новые направления для бронирования",
                    "WB вводит обязательную маркировку для одежды"
                ]
                logger.info("   📝 Тестовые данные")
            
            structured_content = ai_processor.structure_content(texts, [])
            post_type = "РЕЗЕРВНЫЕ ДАННЫЕ"
        
        post_content = post_formatter.format_structured_post(structured_content)
        save_post(post_content)
        
        # 3. Отправка поста
        logger.info("3. 📤 ОТПРАВКА ПОСТА...")
        success = await telegram_manager.send_message(post_content)
        
        # 4. Статистика
        stats_text = generate_stats_text(channel_stats, len(all_messages), post_type, success)
        logger.info(f"🎯 ИТОГ: {stats_text}")
        
        return f"""
        <h2>🎯 Результат выполнения</h2>
        <p><strong>Тип поста:</strong> {post_type}</p>
        <p><strong>Реальных сообщений:</strong> {len(all_messages)}</p>
        <p><strong>Отправка:</strong> {'✅ Успешно' if success else '❌ Не удалось'}</p>
        
        <h3>📊 Статистика парсинга:</h3>
        <pre>{stats_text}</pre>
        
        <h3>📝 Содержание поста:</h3>
        <pre>{post_content[:500]}...</pre>
        
        <p><strong>📋 Подробные логи в Render Dashboard</strong></p>
        <a href="/">← Назад</a>
        """
        
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")
        import traceback
        logger.error(f"🔍 Детали: {traceback.format_exc()}")
        return f"❌ Ошибка: {str(e)}"

def generate_stats_text(channel_stats, total_messages, post_type, send_success):
    """Генерирует текстовую статистику"""
    lines = []
    lines.append(f"ТИП ПОСТА: {post_type}")
    lines.append(f"ВСЕГО СООБЩЕНИЙ: {total_messages}")
    lines.append(f"ОТПРАВКА: {'✅ УСПЕШНО' if send_success else '❌ НЕ УДАЛОСЬ'}")
    lines.append("")
    lines.append("СТАТИСТИКА ПО КАНАЛАМ:")
    lines.append("-" * 40)
    
    successful_parses = 0
    for stat in channel_stats:
        if stat.get('success'):
            successful_parses += 1
            lines.append(f"✅ {stat['channel']}")
            lines.append(f"   📝 {stat['title']}")
            lines.append(f"   📨 Новых: {stat['new_messages']}")
        else:
            lines.append(f"❌ {stat.get('channel', 'N/A')}")
            lines.append(f"   💥 {stat.get('error', 'Unknown error')}")
        lines.append("")
    
    lines.append(f"УСПЕШНЫХ ПАРСИНГОВ: {successful_parses}/{len(channel_stats)}")
    
    return "\n".join(lines)