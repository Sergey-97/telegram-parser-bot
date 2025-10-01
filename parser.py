from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import asyncio
from datetime import datetime, timedelta
from database import Session, Post
from config import API_ID, API_HASH, SOURCE_CHANNELS, DISCUSSION_CHANNELS, PARSE_INTERVAL_DAYS, MAX_POSTS_PER_CHANNEL
import re
import logging

logger = logging.getLogger(__name__)

class ChannelParser:
    def __init__(self, api_id, api_hash):
        self.client = TelegramClient('parser_session', api_id, api_hash)
        self.processed_count = 0
        
    async def connect(self):
        await self.client.start()
        logger.info("Парсер подключен к Telegram")
    
    async def parse_channel(self, channel, days_back=7):
        """Парсит сообщения из канала за указанный период"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        posts = []
        message_count = 0
        
        try:
            async for message in self.client.iter_messages(channel, offset_date=end_date, reverse=False, limit=MAX_POSTS_PER_CHANNEL):
                if message.date.replace(tzinfo=None) < start_date:
                    break
                    
                message_count += 1
                
                # Пропускаем сообщения без текста
                if not message.text:
                    continue
                    
                # Очищаем текст от лишних пробелов и переносов
                clean_text = re.sub(r'\s+', ' ', message.text).strip()
                
                # Фильтруем слишком короткие сообщения и рекламу
                if len(clean_text) > 100 and not self._is_advertisement(clean_text):
                    posts.append({
                        'channel': channel,
                        'message_id': message.id,
                        'text': clean_text,
                        'date': message.date.replace(tzinfo=None)
                    })
                        
        except Exception as e:
            logger.error(f"Ошибка при парсинге канала {channel}: {e}")
            
        logger.info(f"Канал {channel}: обработано {message_count} сообщений, сохранено {len(posts)} постов")
        return posts
    
    def _is_advertisement(self, text):
        """Проверяет, является ли текст рекламой"""
        ad_keywords = ['реклама', 'sponsored', 'промо', 'покупка', 'купить', 'заказать', 'скидка', 'акция']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in ad_keywords)
    
    async def parse_all_channels(self):
        """Парсит все каналы из конфигурации"""
        await self.connect()
        
        all_posts = []
        
        # Парсим основные каналы
        for channel in SOURCE_CHANNELS:
            logger.info(f"Парсим основной канал: {channel}")
            posts = await self.parse_channel(channel, PARSE_INTERVAL_DAYS)
            all_posts.extend(posts)
            await asyncio.sleep(2)  # Задержка между запросами
            
        # Парсим каналы для обсуждений
        for channel in DISCUSSION_CHANNELS:
            logger.info(f"Парсим канал обсуждений: {channel}")
            posts = await self.parse_channel(channel, PARSE_INTERVAL_DAYS)
            all_posts.extend(posts)
            await asyncio.sleep(2)
            
        await self.save_posts(all_posts)
        return all_posts
    
    async def save_posts(self, posts):
        """Сохраняет посты в базу данных"""
        session = Session()
        saved_count = 0
        
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
                    saved_count += 1
            
            session.commit()
            logger.info(f"Сохранено {saved_count} новых постов в базу данных")
            self.processed_count = saved_count
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении постов: {e}")
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
        logger.info(f"Парсинг завершен. Обработано каналов: {len(SOURCE_CHANNELS) + len(DISCUSSION_CHANNELS)}, найдено постов: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        return []
    finally:
        loop.run_until_complete(parser.disconnect())
        loop.close()