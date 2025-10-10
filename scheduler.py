import os
import asyncio
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

def scheduled_post():
    """Функция для планировщика - запускает бота"""
    try:
        logger.info("🕐 Запуск запланированной публикации...")
        
        # Запускаем асинхронную функцию в отдельном event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from bot_runner import run_bot
        result = loop.run_until_complete(run_bot())
        loop.close()
        
        logger.info(f"✅ Запланированная публикация завершена: {result}")
    except Exception as e:
        logger.error(f"❌ Ошибка в запланированной публикации: {e}")

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

# Автоматический запуск планировщика при импорте
scheduler = start_scheduler()