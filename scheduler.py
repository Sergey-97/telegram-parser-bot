import schedule
import time
import threading
from datetime import datetime
from parser import parse_channels_sync
from nlp_processor import NLPProcessor
from database import Session, Post
import logging
import os
from config import DEBUG

logger = logging.getLogger(__name__)

class BotScheduler:
    def __init__(self):
        self.nlp_processor = NLPProcessor()
        self.running = False
        self.last_run = None
        
    def daily_task(self):
        """Ежедневная задача по парсингу и публикации"""
        self.last_run = datetime.now()
        logger.info(f"🚀 Запуск ежедневной задачи: {self.last_run}")
        
        try:
            # Парсим каналы
            logger.info("📡 Начинаем парсинг каналов...")
            parse_result = parse_channels_sync()
            
            # Обрабатываем посты
            logger.info("🤖 Обрабатываем посты...")
            self.process_and_publish()
            
            logger.info("✅ Ежедневная задача завершена успешно")
            
        except Exception as e:
            logger.error(f"❌ Ошибка в ежедневной задаче: {e}")
    
    def process_and_publish(self):
        """Обрабатывает посты и публикует результат"""
        session = Session()
        
        try:
            # Получаем непроцессированные основные посты
            main_posts = session.query(Post).filter(
                Post.is_main_post == True,
                Post.processed == False
            ).order_by(Post.date.desc()).all()
            
            # Получаем все обсуждения для анализа
            discussion_posts = session.query(Post).filter(
                Post.is_main_post == False,
                Post.processed == False
            ).order_by(Post.date.desc()).all()
            
            logger.info(f"📝 Найдено {len(main_posts)} основных постов и {len(discussion_posts)} постов для обсуждений")
            
            if not main_posts:
                logger.info("ℹ️ Нет новых основных постов для обработки")
                return
            
            # Обрабатываем посты через NLP
            final_content = self.nlp_processor.process_posts(main_posts, discussion_posts)
            
            # Логируем результат (временно вместо публикации)
            logger.info(f"📤 Готов к публикации:\n{final_content}")
            
            # Помечаем посты как обработанные
            for post in main_posts + discussion_posts:
                post.processed = True
                post.processed_text = final_content[:500]
                
            session.commit()
            logger.info("✅ Посты успешно обработаны")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке и публикации: {e}")
            session.rollback()
        finally:
            session.close()
    
    def run_scheduler(self):
        """Запускает планировщик"""
        self.running = True
        
        # Настраиваем расписание
        schedule.every().day.at("09:00").do(self.daily_task)  # Утренний парсинг
        schedule.every().day.at("18:00").do(self.daily_task)  # Вечерний парсинг
        
        # Для тестирования - запуск каждые 10 минут в debug режиме
        if DEBUG:
            logger.info("🔧 DEBUG режим: планировщик запускается каждые 10 минут")
            schedule.every(10).minutes.do(self.daily_task)
        
        logger.info(f"⏰ Планировщик запущен. Режим: {'DEBUG' if DEBUG else 'PRODUCTION'}")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)
            except Exception as e:
                logger.error(f"❌ Ошибка в планировщике: {e}")
                time.sleep(60)
    
    def stop_scheduler(self):
        """Останавливает планировщик"""
        self.running = False
        logger.info("🛑 Планировщик остановлен")

def run_scheduler_in_thread():
    """Запускает планировщик в отдельном потоке"""
    scheduler = BotScheduler()
    scheduler_thread = threading.Thread(target=scheduler.run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    logger.info("🧵 Планировщик запущен в отдельном потоке")
    return scheduler