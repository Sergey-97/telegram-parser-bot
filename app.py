import os
import asyncio
import logging
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Инициализация базы данных при запуске
try:
    from database import init_db
    init_db()
    logger.info("✅ База данных инициализирована")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации БД: {e}")

def scheduled_post():
    """Функция для планировщика - запускает бота"""
    try:
        logger.info("🕐 Запуск запланированной публикации...")
        
        # Запускаем асинхронную функцию в отдельном event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from bot_runner import run_bot
        loop.run_until_complete(run_bot())
        loop.close()
        
        logger.info("✅ Запланированная публикация завершена")
    except Exception as e:
        logger.error(f"❌ Ошибка в запланированной публикации: {e}")

@app.route('/')
def home():
    return """
    <h1>🤖 Telegram Parser Bot</h1>
    <p>Бот для автоматической публикации аналитики маркетплейсов</p>
    <p><strong>Расписание:</strong> Каждый понедельник в 10:00 UTC</p>
    <p><strong>Статус:</strong> ✅ Активен</p>
    <p>
        <a href="/health">Health Check</a> | 
        <a href="/run-now">Run Now</a> |
        <a href="/logs">View Logs</a>
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

@app.route('/logs')
def show_logs():
    """Показывает последние логи (для отладки)"""
    try:
        # В Render логи доступны через dashboard
        return """
        <h2>📋 Logs</h2>
        <p>Логи доступны в Render Dashboard:</p>
        <ol>
            <li>Перейдите в ваш сервис на Render</li>
            <li>Нажмите на вкладку "Logs"</li>
            <li>Посмотрите логи выполнения</li>
        </ol>
        <a href="/">← Назад</a>
        """
    except Exception as e:
        return f"Error: {str(e)}"

def start_scheduler():
    """Запуск планировщика"""
    try:
        scheduler = BackgroundScheduler()
        
        # Публикация каждый понедельник в 10:00 UTC
        trigger = CronTrigger(
            day_of_week='mon',  # Понедельник
            hour=10,            # 10:00
            minute=0,           # 00 минут
            timezone='UTC'
        )
        
        scheduler.add_job(
            func=scheduled_post,
            trigger=trigger,
            id='weekly_post',
            name='Weekly marketplace analysis post',
            replace_existing=True
        )
        
        # Для отладки: ежедневный запуск в 11:00 если включен DEBUG
        if os.getenv('DEBUG_SCHEDULE', 'false').lower() == 'true':
            scheduler.add_job(
                func=scheduled_post,
                trigger=CronTrigger(hour=11, minute=0, timezone='UTC'),
                id='daily_test',
                name='Daily test post'
            )
            logger.info("🔧 Режим отладки: ежедневный запуск в 11:00 UTC")
        
        scheduler.start()
        logger.info("📅 Планировщик запущен: понедельник 10:00 UTC")
        
        return scheduler
    except Exception as e:
        logger.error(f"❌ Ошибка запуска планировщика: {e}")
        return None

# Глобальная переменная для хранения планировщика
scheduler = None

@app.before_first_request
def initialize():
    """Инициализация при первом запросе"""
    global scheduler
    scheduler = start_scheduler()

if __name__ == '__main__':
    # Инициализируем при прямом запуске
    scheduler = start_scheduler()
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)