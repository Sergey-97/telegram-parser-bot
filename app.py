import os
import asyncio
import logging
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pyrogram import Client
from database import init_db
from bot_runner import run_bot

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Инициализация базы данных при запуске
init_db()

def scheduled_post():
    """Функция для планировщика - запускает бота"""
    try:
        logger.info("🕐 Запуск запланированной публикации...")
        asyncio.run(run_bot())
        logger.info("✅ Запланированная публикация завершена")
    except Exception as e:
        logger.error(f"❌ Ошибка в запланированной публикации: {e}")

@app.route('/')
def home():
    return "🤖 Telegram Parser Bot is running! Posts scheduled for Mondays 10:00 UTC"

@app.route('/health')
def health():
    return "OK"

@app.route('/run-now')
def run_now():
    """Ручной запуск бота"""
    try:
        asyncio.run(run_bot())
        return "✅ Bot executed successfully!"
    except Exception as e:
        return f"❌ Error: {e}"

def start_scheduler():
    """Запуск планировщика"""
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
    
    # Дополнительно: тестовый запуск каждый день в 11:00 для отладки
    if os.getenv('DEBUG_SCHEDULE', 'False').lower() == 'true':
        scheduler.add_job(
            func=scheduled_post,
            trigger=CronTrigger(hour=11, minute=0, timezone='UTC'),
            id='daily_test',
            name='Daily test post'
        )
    
    scheduler.start()
    logger.info("📅 Планировщик запущен: понедельник 10:00 UTC")

if __name__ == '__main__':
    # Запускаем планировщик при старте приложения
    start_scheduler()
    
    # Запускаем Flask приложение
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)