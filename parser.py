from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import asyncio
from datetime import datetime, timedelta
from database import Session, Post
from config import API_ID, API_HASH, SOURCE_CHANNELS, DISCUSSION_CHANNELS, PARSE_INTERVAL_DAYS
import re

class ChannelParser:
    def __init__(self, api_id, api_hash):
        self.client = TelegramClient('parser_session', api_id, api_hash)
        
    async def connect(self):
        await self.client.start()
        print("Парсер подключен к Telegram")
    
    async def parse_channel(self, channel, days_back=7):
        """Парсит сообщения из канала за указанный период"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        posts = []
        
        try:
            async for message in self.client.iter_messages(channel, offset_date=end_date, reverse=False):
                if message.date < start_date:
                    break
                    
                if message.text:
                    # Очищаем текст от лишних пробелов и переносов
                    clean_text = re.sub(r'\s+', ' ', message.text).strip()
                    
                    if len(clean_text) > 50:  # Игнорируем слишком короткие сообщения
                        posts.append({
                            'channel': channel,
                            'message_id': message.id,
                            'text': clean_text,
                            'date': message.date
                        })
                        
        except Exception as e:
            print(f"Ошибка при парсинге канала {channel}: {e}")
            
        return posts
    
    async def parse_all_channels(self):
        """Парсит все каналы из конфигурации"""
        await self.connect()
        
        all_posts = []
        
        # Парсим основные каналы
        for channel in SOURCE_CHANNELS:
            print(f"Парсим канал: {channel}")
            posts = await self.parse_channel(channel, PARSE_INTERVAL_DAYS)
            all_posts.extend(posts)
            await asyncio.sleep(1)  # Задержка между запросами
            
        # Парсим каналы для обсуждений
        for channel in DISCUSSION_CHANNELS:
            print(f"Парсим канал обсуждений: {channel}")
            posts = await self.parse_channel(channel, PARSE_INTERVAL_DAYS)
            all_posts.extend(posts)
            await asyncio.sleep(1)
            
        await self.save_posts(all_posts)
        return all_posts
    
    async def save_posts(self, posts):
        """Сохраняет посты в базу данных"""
        session = Session()
        
        try:
            for post_data in posts:
                # Проверяем, существует ли уже такой пост
                existing_post = session.query(Post).filter_by(
                    channel=post_data['channel'],
                    message_id=post_data['message_id']
                ).first()
                
                if not existing_post:
                    new_post = Post(
                        channel=post_data['channel'],
                        message_id=post_data['message_id'],
                        text=post_data['text'],
                        date=post_data['date']
                    )
                    session.add(new_post)
            
            session.commit()
            print(f"Сохранено {len(posts)} постов в базу данных")
            
        except Exception as e:
            print(f"Ошибка при сохранении постов: {e}")
            session.rollback()
        finally:
            session.close()
    
    async def disconnect(self):
        await self.client.disconnect()

# Синхронная обертка для использования в планировщике
def parse_channels_sync():
    parser = ChannelParser(API_ID, API_HASH)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(parser.parse_all_channels())
        return result
    finally:
        loop.run_until_complete(parser.disconnect())
        loop.close()