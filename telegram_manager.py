import asyncio
import logging
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN, TARGET_CHANNEL

logger = logging.getLogger(__name__)

class TelegramManager:
    def __init__(self):
        self.user_client = None
        self.bot_client = None
    
    async def get_user_client(self):
        """Возвращает пользовательского клиента для парсинга"""
        if self.user_client is None:
            self.user_client = Client(
                "telegram_parser",
                api_id=API_ID,
                api_hash=API_HASH,
                workdir="/opt/render/project/src"
            )
            await self.user_client.start()
            
            me = await self.user_client.get_me()
            logger.info(f"🔐 ПОЛЬЗОВАТЕЛЬ: {me.first_name} - Бот: {me.is_bot}")
            
        return self.user_client
    
    async def get_bot_client(self):
        """Возвращает бот клиента для отправки"""
        if self.bot_client is None and BOT_TOKEN:
            self.bot_client = Client(
                "telegram_bot",
                api_id=API_ID,
                api_hash=API_HASH,
                bot_token=BOT_TOKEN,
                workdir="/opt/render/project/src"
            )
            await self.bot_client.start()
            
            me = await self.bot_client.get_me()
            logger.info(f"🤖 БОТ: {me.username} - Бот: {me.is_bot}")
            
        return self.bot_client
    
    async def send_message(self, text):
        """Отправляет сообщение через бота"""
        try:
            bot = await self.get_bot_client()
            if bot:
                # Ограничиваем длину
                max_length = 4096
                if len(text) > max_length:
                    text = text[:max_length-100] + "\n\n... (пост сокращен)"
                
                await bot.send_message(TARGET_CHANNEL, text)
                logger.info(f"✅ Сообщение отправлено в {TARGET_CHANNEL}")
                return True
            else:
                logger.warning("⚠️ Бот не доступен для отправки")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка отправки: {e}")
            return False
    
    async def cleanup(self):
        """Очистка клиентов"""
        if self.user_client:
            await self.user_client.stop()
        if self.bot_client:
            await self.bot_client.stop()

# Глобальный экземпляр
telegram_manager = TelegramManager()