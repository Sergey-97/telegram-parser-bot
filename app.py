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

@app.route('/run-bot')
def run_bot():
    """Полный запуск бота"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from bot_runner import run_bot
        result = loop.run_until_complete(run_bot())
        loop.close()
        
        return result
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

@app.route('/test-parser')
def test_parser():
    """Тест парсинга без отправки"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from simple_parser import parse_all_channels_simple
        result = loop.run_until_complete(parse_all_channels_simple())
        loop.close()
        
        stats = result['stats']
        messages = result['messages']
        
        html_result = f"""
        <h2>🧪 Тест парсинга</h2>
        <p><strong>Найдено сообщений:</strong> {len(messages)}</p>
        
        <h3>📊 Статистика:</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th>Канал</th>
                <th>Статус</th>
                <th>Сообщений</th>
                <th>Детали</th>
            </tr>
        """
        
        for stat in stats:
            if stat.get('success'):
                status = "✅ Успешно"
                details = f"Новых: {stat['new_messages']}"
            else:
                status = "❌ Ошибка"
                details = stat.get('error', 'Unknown')
            
            html_result += f"""
            <tr>
                <td>{stat.get('channel', 'N/A')}</td>
                <td>{status}</td>
                <td>{stat.get('new_messages', 0)}</td>
                <td>{details}</td>
            </tr>
            """
        
        html_result += "</table>"
        
        if messages:
            html_result += f"""
            <h3>📝 Примеры сообщений:</h3>
            <ol>
            {"".join([f"<li>{msg[:150]}...</li>" for msg in messages[:5]])}
            </ol>
            """
        
        html_result += '<a href="/">← Назад</a>'
        return html_result
        
    except Exception as e:
        return f"❌ Ошибка теста: {str(e)}"

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