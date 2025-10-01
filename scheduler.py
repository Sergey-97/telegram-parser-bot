import schedule
import time
import threading
from datetime import datetime
from parser import parse_channels_sync
from nlp_processor import NLPProcessor
from database import Session, Post
from bot import publish_post
import asyncio
import logging
import os

logger = logging.getLogger(__name__)

class BotScheduler:
    def __init__(self):
        self.nlp_processor = NLPProcessor()
        self.running = False
        
    def daily_task(self):
        """Ежедневная задача по парсингу и публикации"""
        logger.info(f"Запуск ежедневной задачи: {datetime.now()}")
        
        try:
            # Парсим каналы
            logger.info("Начинаем парсинг каналов...")
            parse_channels_sync()
            
            # Обрабатываем посты
            logger.info("Обрабатываем посты...")
            self.process_and_publish()
            
            logger.info("Ежедневная задача завершена успешно")
            
        except Exception as e:
            logger.error(f"Ошибка в ежедневной задаче: {e}")
    
    def process_and_publish(self):
        """Обрабатывает посты и публикует результат"""
        from config import SOURCE_CHANNELS, DISCUSSION_CHANNELS
        
        session = Session()
        
        try:
            # Получаем непроцессированные посты за указанный период
            main_posts = session.query(Post).filter(
                Post.channel.in_(SOURCE_CHANNELS),
                Post.processed == False
            ).all()
            
            discussion_posts = session.query(Post).filter(
                Post.channel.in_(DISCUSSION_CHANNELS),
                Post.processed == False
            ).all()
            
            if not main_posts and not discussion_posts:
                logger.info("Нет новых постов для обработки")
                return
            
            logger.info(f"Найдено {len(main_posts)} основных постов и {len(discussion_posts)} постов для обсуждений")
            
            # Обрабатываем посты через NLP
            final_content = self.nlp_processor.process_posts(main_posts, discussion_posts)
            
            # Публикуем пост
            asyncio.run(publish_post(final_content))
            
            # Помечаем посты как обработанные
            for post in main_posts + discussion_posts:
                post.processed = True
                post.processed_text = final_content
                
            session.commit()
            logger.info("Посты успешно обработаны и опубликованы")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке и публикации: {e}")
            session.rollback()
        finally:
            session.close()
    
    def run_scheduler(self):
        """Запускает планировщик"""
        self.running = True
        
        # Настраиваем расписание
        schedule.every().day.at("09:00").do(self.daily_task)  # Парсинг в 9:00
        schedule.every().day.at("10:00").do(self.daily_task)  # Публикация в 10:00
        
        # Для тестирования - запуск каждые 10 минут
        if os.environ.get('DEBUG', False):
            schedule.every(10).minutes.do(self.daily_task)
        
        logger.info("Планировщик запущен")
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Проверяем каждую минуту
    
    def stop_scheduler(self):
        """Останавливает планировщик"""
        self.running = False

def run_scheduler_in_thread():
    """Запускает планировщик в отдельном потоке"""
    scheduler = BotScheduler()
    scheduler_thread = threading.Thread(target=scheduler.run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    return scheduler