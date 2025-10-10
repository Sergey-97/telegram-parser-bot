import os
import asyncio
import logging
from flask import Flask

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Инициализация базы данных
try:
    from database import init_db
    init_db()
    logger.info("✅ База данных инициализирована")
except Exception as e:
    logger.error(f"❌ Ошибка БД: {e}")

@app.route('/')
def home():
    return """
    <h1>🤖 Telegram Parser Bot</h1>
    <p>Бот для автоматической публикации аналитики маркетплейсов</p>
    
    <h3>🚀 Действия:</h3>
    <ul>
        <li><a href="/run-bot">/run-bot</a> - Полный запуск парсера</li>
        <li><a href="/test-parser">/test-parser</a> - Тест парсинга</li>
        <li><a href="/test-send">/test-send</a> - Тест отправки</li>
        <li><a href="/health">/health</a> - Проверка работы</li>
    </ul>
    
    <h3>📊 Каналы для парсинга:</h3>
    <ul>
        <li>@ozonmarketplace</li>
        <li>@wbsellerofficial</li>
        <li>@ozon_adv</li>
        <li>@sklad1313</li>
        <li>@sellmonitor_com</li>
    </ul>
    
    <p><strong>Статус:</strong> ✅ Telegram функциональность добавлена</p>
    """

@app.route('/health')
def health():
    return "✅ Сервер работает"

@app.route('/run-advanced')
def run_advanced():
    """Запуск улучшенного бота"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from advanced_bot_runner import run_advanced_bot
        result = loop.run_until_complete(run_advanced_bot())
        loop.close()
        
        return result
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

@app.route('/parsing-stats')
def parsing_stats():
    """Статистика парсинга"""
    try:
        from parsing_state import get_parsing_stats, is_first_run
        
        stats = get_parsing_stats()
        first_run = is_first_run()
        
        return f"""
        <h2>📊 Статистика парсинга</h2>
        
        <div style="background: #f0f8ff; padding: 15px; border-radius: 10px;">
            <p><strong>🎯 Режим:</strong> {'🆕 ПЕРВЫЙ ЗАПУСК' if first_run else '🔄 РЕГУЛЯРНЫЙ ПАРСИНГ'}</p>
            <p><strong>🌐 Обработано каналов:</strong> {stats['total_channels']}</p>
            <p><strong>📨 Всего сообщений в базе:</strong> {stats['total_messages_parsed']}</p>
        </div>
        
        <p><strong>💡 Совет:</strong> {'Запустите парсинг для наполнения базы данных' if first_run else 'База данных уже содержит исторические данные'}</p>
        
        <a href="/run-advanced">🚀 Запустить улучшенный парсинг</a> | 
        <a href="/">← Назад</a>
        """
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

@app.route('/test-send')
def test_send():
    """Тест отправки сообщения"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from telegram_manager import telegram_manager
        from post_formatter import PostFormatter
        
        # Создаем тестовый пост
        formatter = PostFormatter()
        test_post = formatter._create_fallback_post()
        
        # Отправляем
        success = loop.run_until_complete(telegram_manager.send_message(test_post))
        loop.run_until_complete(telegram_manager.cleanup())
        loop.close()
        
        if success:
            return """
            <h2>✅ Тест отправки успешен!</h2>
            <p>Тестовое сообщение отправлено в канал.</p>
            <a href="/">← Назад</a>
            """
        else:
            return """
            <h2>❌ Тест отправки не удался</h2>
            <p>Проверьте BOT_TOKEN и права бота в канале.</p>
            <a href="/">← Назад</a>
            """
            
    except Exception as e:
        return f"❌ Ошибка отправки: {str(e)}"

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)