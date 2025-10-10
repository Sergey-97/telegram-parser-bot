import os
import asyncio
import logging
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

logger = logging.getLogger(__name__)

class AuthSystem:
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
            logger.info(f"🔐 ПОЛЬЗОВАТЕЛЬ: {me.first_name} (@{me.username}) - Бот: {me.is_bot}")
            
        return self.user_client
    
    async def get_bot_client(self):
        """Возвращает бот клиента для отправки сообщений"""
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
            logger.info(f"🤖 БОТ: {me.first_name} (@{me.username}) - Бот: {me.is_bot}")
            
        return self.bot_client
    
    async def cleanup(self):
        """Очистка клиентов"""
        if self.user_client:
            await self.user_client.stop()
        if self.bot_client:
            await self.bot_client.stop()

# Глобальный экземпляр
auth_system = AuthSystem()