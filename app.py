import os
import asyncio
import logging
from flask import Flask

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
    <h1>🤖 Telegram Parser Bot - РЕАЛЬНЫЙ ПАРСИНГ</h1>
    <p>Бот для парсинга реальных данных с Telegram каналов</p>
    
    <h3>🚀 Действия:</h3>
    <ul>
        <li><a href="/run-now">/run-now</a> - Запуск с пользовательской сессией</li>
        <li><a href="/health">/health</a> - Проверка работы</li>
        <li><a href="/test-parsing">/test-parsing</a> - Тест парсинга</li>
    </ul>
    
    <h3>📊 Каналы для парсинга:</h3>
    <ul>
        <li>@ozonmarketplace</li>
        <li>@wbsellerofficial</li>
        <li>@ozon_adv</li>
        <li>@sklad1313</li>
        <li>@sellmonitor_com</li>
        <li>@redmilliard</li>
        <li>@marketplace_hogwarts</li>
        <li>@mpgo_ru</li>
        <li>@ProdaemWB</li>
        <li>@ProdaemOZON</li>
    </ul>
    
    <p><strong>✅ Используется пользовательская сессия для парсинга</strong></p>
    """

@app.route('/health')
def health():
    return "✅ Сервер работает"

@app.route('/run-now')
def run_now():
    """Запуск бота с пользовательской сессией"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from bot_runner import run_bot
        result = loop.run_until_complete(run_bot())
        loop.close()
        
        return result
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

@app.route('/test-parsing')
def test_parsing():
    """Тест парсинга пользовательской сессией"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from bot_runner import parse_channels_with_user
        from pyrogram import Client
        from config import API_ID, API_HASH
        
        user_client = Client("telegram_parser", api_id=API_ID, api_hash=API_HASH)
        
        async def test():
            await user_client.start()
            result = await parse_channels_with_user(user_client)
            await user_client.stop()
            return result
        
        parsing_result = loop.run_until_complete(test())
        loop.close()
        
        stats = parsing_result['stats']
        messages = parsing_result['messages']
        
        html_result = f"""
        <h2>🧪 Тест парсинга пользовательской сессией</h2>
        <p><strong>Найдено сообщений:</strong> {len(messages)}</p>
        
        <h3>📊 Статистика доступа:</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th>Канал</th>
                <th>Статус</th>
                <th>Сообщений</th>
                <th>Детали</th>
            </tr>
        """
        
        for channel, data in stats.items():
            if data.get('success'):
                status = "✅ Доступен"
                details = f"Новых: {data.get('new_messages', 0)}"
            else:
                status = "❌ Ошибка"
                details = data.get('error', 'Unknown')
            
            html_result += f"""
            <tr>
                <td>{channel}</td>
                <td>{status}</td>
                <td>{data.get('new_messages', 0)}</td>
                <td>{details}</td>
            </tr>
            """
        
        html_result += "</table>"
        
        if messages:
            html_result += f"""
            <h3>📝 Примеры сообщений ({len(messages)} всего):</h3>
            <ol>
            {"".join([f"<li>{msg[:150]}...</li>" for msg in messages[:5]])}
            </ol>
            """
        
        html_result += '<a href="/">← Назад</a>'
        return html_result
        
    except Exception as e:
        return f"❌ Ошибка теста: {str(e)}"

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)