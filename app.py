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
        <li><a href="/run-now">/run-now</a> - Запуск реального парсинга</li>
        <li><a href="/health">/health</a> - Проверка работы</li>
        <li><a href="/test-parsing">/test-parsing</a> - Тест парсинга (без отправки)</li>
    </ul>
    
    <h3>📊 Каналы для парсинга:</h3>
    <ul>
        <li>@ozonmarketplace</li>
        <li>@wbsellerofficial</li>
        <li>@ozon_adv</li>
        <li>@sklad1313</li>
        <li>@sellmonitor_com</li>
        <li>и другие...</li>
    </ul>
    """

@app.route('/health')
def health():
    return "✅ Сервер работает"

@app.route('/run-now')
def run_now():
    """Запуск бота с реальным парсингом"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from bot_runner import run_bot
        result = loop.run_until_complete(run_bot())
        loop.close()
        
        return f"""
        <h2>🎯 Результат выполнения:</h2>
        <p>{result}</p>
        <p><strong>📋 Проверьте логи в Render Dashboard для деталей парсинга</strong></p>
        <a href="/">← Назад</a>
        """
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"

@app.route('/test-parsing')
def test_parsing():
    """Тест парсинга без отправки поста"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from bot_runner import parse_all_channels
        from pyrogram import Client
        from config import API_ID, API_HASH, BOT_TOKEN
        
        client = Client("test_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
        
        async def test_parse():
            await client.start()
            messages = await parse_all_channels(client)
            await client.stop()
            return messages
        
        messages = loop.run_until_complete(test_parse())
        loop.close()
        
        return f"""
        <h2>🧪 Тест парсинга</h2>
        <p><strong>Найдено сообщений:</strong> {len(messages)}</p>
        
        <h3>📝 Примеры сообщений:</h3>
        <ol>
        {"".join([f"<li>{msg[:200]}...</li>" for msg in messages[:5]])}
        </ol>
        
        <a href="/">← Назад</a>
        """
    except Exception as e:
        return f"❌ Ошибка теста: {str(e)}"

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)