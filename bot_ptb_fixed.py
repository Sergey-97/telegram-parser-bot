# bot_ptb_fixed.py
import logging
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
from ai_processor_final import AIProcessorFinal
from post_formatter import PostFormatter

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
        self.source_channels = [ch.strip() for ch in os.getenv('SOURCE_CHANNELS', '').split(',') if ch.strip()]
        
        if not self.token:
            raise ValueError("BOT_TOKEN не найден в .env")
        
        # Создаем updater (старый стиль для версии 13.15)
        self.updater = Updater(token=self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        
        # Добавляем обработчики команд
        self.dispatcher.add_handler(CommandHandler("start", self.start_command))
        self.dispatcher.add_handler(CommandHandler("parse", self.parse_command))
        self.dispatcher.add_handler(CommandHandler("status", self.status_command))
    
    def start_command(self, update: Update, context: CallbackContext):
        """Обработчик команды /start"""
        update.message.reply_text(
            "🤖 Бот-парсер активен!\n\n"
            "Команды:\n"
            "/parse - запустить парсинг и публикацию\n"
            "/status - статус бота"
        )
    
    def parse_command(self, update: Update, context: CallbackContext):
        """Обработчик команды /parse"""
        update.message.reply_text("🔄 Запускаю AI-парсинг...")
        
        try:
            # Здесь будет логика сбора и обработки постов
            # Пока используем тестовые данные
            main_posts = [
                "Ozon запускает новую программу лояльности для продавцов. Теперь участники маркетплейса смогут получать дополнительные бонусы за объем продаж и положительные отзывы.",
                "Скидки до 50% на электронику в этом месяце! Успейте приобрести смартфоны, ноутбуки и планшеты по выгодным ценам. Акция действует до конца месяца."
            ]
            
            discussion_posts = [
                "Отличная новость про Ozon! Я как продавец очень доволен новыми условиями программы лояльности.",
                "Скидки на электронику просто супер! Уже присмотрел себе новый ноутбук по отличной цене.",
                "Были небольшие проблемы с доставкой, но в целом сервис улучшается."
            ]
            
            # AI-обработка
            structured_content = ai_processor.structure_content(main_posts, discussion_posts)
            
            # Форматирование поста
            final_post = post_formatter.format_structured_post(
                structured_content, 
                self.source_channels
            )
            
            # Публикация в канал
            context.bot.send_message(
                chat_id=self.target_channel,
                text=final_post,
                parse_mode='Markdown'
            )
            
            update.message.reply_text("✅ AI-пост успешно опубликован в канал!")
            
        except Exception as e:
            logger.error(f"Ошибка парсинга: {e}")
            update.message.reply_text(f"❌ Ошибка: {e}")
    
    def status_command(self, update: Update, context: CallbackContext):
        """Обработчик команды /status"""
        status_text = (
            "🤖 **Статус бота:** Активен\n"
            f"🎯 **Целевой канал:** {self.target_channel}\n"
            f"📡 **Источники:** {len(self.source_channels)}\n"
            f"🧠 **AI-процессор:** Готов\n"
            "⏰ **Используйте /parse для запуска**"
        )
        update.message.reply_text(status_text, parse_mode='Markdown')
    
    def publish_to_channel(self, text: str):
        """Публикация сообщения в канал"""
        try:
            self.updater.bot.send_message(
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
        
        try:
            # Тестовая публикация при запуске
            self.updater.bot.send_message(
                chat_id=self.target_channel,
                text="🚀 AI-парсер запущен и готов к работе!",
                parse_mode='Markdown'
            )
            logger.info("✅ Стартовое сообщение отправлено")
        except Exception as e:
            logger.error(f"⚠️ Не удалось отправить стартовое сообщение: {e}")
        
        # Запускаем бота
        self.updater.start_polling()
        logger.info("🤖 Бот запущен и ожидает команды...")
        self.updater.idle()

if __name__ == "__main__":
    try:
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")