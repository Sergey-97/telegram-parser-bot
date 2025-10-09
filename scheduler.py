import os
import asyncio
import logging
from flask import Flask

# Импортируем планировщик (он запустится автоматически)
import scheduler

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
    logger.error(f"❌ Ошибка инициализации БД: {e}")

@app.route('/')
def home():
    return """
    <h1>🤖 Telegram Parser Bot</h1>
    <p>Бот для автоматической публикации аналитики маркетплейсов</p>
    <p><strong>Расписание:</strong> Каждый понедельник в 10:00 UTC</p>
    <p><strong>Статус:</strong> ✅ Активен</p>
    <p>
        <a href="/health">Health Check</a> | 
        <a href="/run-now">Run Now</a>
    </p>
    """

@app.route('/health')
def health():
    return "OK"

@app.route('/run-now')
def run_now():
    """Ручной запуск бота"""
    try:
        # Запускаем в отдельном event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from bot_runner import run_bot
        loop.run_until_complete(run_bot())
        loop.close()
        
        return "✅ Bot executed successfully! Check Render logs for details."
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)