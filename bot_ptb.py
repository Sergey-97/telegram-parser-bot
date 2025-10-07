# bot_ptb.py
import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from ai_processor_final import AIProcessorFinal
from post_formatter import PostFormatter
import asyncio

# Загрузка конфигурации
load_dotenv()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация компонентов
ai_processor = AIProcessorFinal()
post_formatter = PostFormatter()

class TelegramBot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN')
        self.target_channel = os.getenv('TARGET_CHANNEL', '@mar_factor')
        self.source_channels = os.getenv('SOURCE_CHANNELS', '').split(',')
        
        if not self.token:
            raise ValueError("BOT_TOKEN не найден в .env")
        
        # Создаем приложение
        self.application = Application.builder().token(self.token).build()
        
        # Добавляем обработчики команд
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("parse", self.parse_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        await update.message.reply_text(
            "🤖 Бот-парсер активен!\n\n"
            "Команды:\n"
            "/parse - запустить парсинг и публикацию\n"
            "/status - статус бота"
        )
    
    async def parse_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /parse"""
        await update.message.reply_text("🔄 Запускаю AI-парсинг...")
        
        try:
            # Здесь будет логика сбора и обработки постов
            # Пока используем тестовые данные
            main_posts = [
                "Ozon запускает новую программу лояльности для продавцов. Теперь участники маркетплейса смогут получать дополнительные бонусы.",
                "Скидки до 50% на электронику в этом месяце! Успейте приобрести технику по выгодным ценам."
            ]
            
            discussion_posts = [
                "Отличная новость про Ozon! Я как продавец очень доволен новыми условиями.",
                "Скидки на электронику просто супер! Уже присмотрел себе новый ноутбук."
            ]
            
            # AI-обработка
            structured_content = ai_processor.structure_content(main_posts, discussion_posts)
            
            # Форматирование поста
            final_post = post_formatter.format_structured_post(
                structured_content, 
                self.source_channels
            )
            
            # Публикация в канал
            await context.bot.send_message(
                chat_id=self.target_channel,
                text=final_post,
                parse_mode='Markdown'
            )
            
            await update.message.reply_text("✅ AI-пост успешно опубликован!")
            
        except Exception as e:
            logger.error(f"Ошибка парсинга: {e}")
            await update.message.reply_text(f"❌ Ошибка: {e}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        status_text = (
            "🤖 **Статус бота:** Активен\n"
            f"🎯 **Целевой канал:** {self.target_channel}\n"
            f"📡 **Источники:** {len(self.source_channels)}\n"
            f"🧠 **AI-процессор:** Готов\n"
            "⏰ **Используйте /parse для запуска**"
        )
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def publish_to_channel(self, text: str):
        """Публикация сообщения в канал"""
        try:
            await self.application.bot.send_message(
                chat_id=self.target_channel,
                text=text,
                parse_mode='Markdown'
            )
            logger.info(f"✅ Сообщение опубликовано в {self.target_channel}")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка публикации: {e}")
            return False
    
    def run(self):
        """Запуск бота"""
        logger.info("🚀 Запуск бота...")
        
        # Тестовая публикация при запуске
        async def post_startup_message():
            try:
                await self.application.bot.send_message(
                    chat_id=self.target_channel,
                    text="🚀 AI-парсер запущен и готов к работе!",
                    parse_mode='Markdown'
                )
                logger.info("✅ Стартовое сообщение отправлено")
            except Exception as e:
                logger.error(f"❌ Ошибка отправки стартового сообщения: {e}")
        
        # Добавляем задачу при запуске
        self.application.post_init = post_startup_message
        
        # Запускаем бота
        self.application.run_polling()

if __name__ == "__main__":
    try:
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")