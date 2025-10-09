# parser.py
import asyncio
import logging
import hashlib
from pyrogram import Client
from pyrogram.errors import ChannelInvalid, ChannelPrivate, FloodWait
from datetime import datetime, timedelta
import config
from database import save_processed_message, is_message_processed, update_stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Parser:
    def __init__(self):
        self.app = None
    
    async def initialize(self):
        self.app = Client("parser_session", config.API_ID, config.API_HASH)
        await self.app.start()
        print("✅ Pyrogram клиент запущен")
    
    async def shutdown(self):
        if self.app:
            await self.app.stop()
            print("✅ Pyrogram клиент остановлен")
    
    def detect_marketplace(self, text: str) -> str:
        """Определяет к какому маркетплейсу относится сообщение"""
        text_lower = text.lower()
        
        for marketplace, keywords in config.MARKETPLACE_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                return marketplace
        
        return 'other'
    
    def create_message_id(self, channel: str, message_id: int) -> str:
        """Создает уникальный ID сообщения"""
        return f"{channel}_{message_id}"
    
    async def parse_channel_messages(self, channel_username: str, limit: int, is_source: bool = True):
        """Парсит сообщения из канала с фильтрацией дубликатов"""
        try:
            clean_username = channel_username.replace('https://t.me/', '').replace('@', '')
            
            print(f"🔍 Парсим {channel_username} (лимит: {limit})...")
            
            messages_data = []
            new_messages_count = 0
            duplicate_count = 0
            
            async for message in self.app.get_chat_history(clean_username, limit=limit):
                # Пропускаем сообщения без текста или слишком короткие
                if not message.text or len(message.text.strip()) < 15:
                    continue
                
                # Пропускаем служебные сообщения
                if any(word in message.text.lower() for word in ['присоединился', 'покинул', 'admin', 'админ']):
                    continue
                
                # Создаем уникальный ID и проверяем дубликат
                message_id = self.create_message_id(clean_username, message.id)
                if is_message_processed(message_id, clean_username):
                    duplicate_count += 1
                    continue
                
                # Определяем маркетплейс
                marketplace = self.detect_marketplace(message.text)
                
                # Очищаем текст
                clean_text = self.clean_message_text(message.text)
                
                # Сохраняем сообщение
                messages_data.append({
                    'text': clean_text,
                    'date': message.date,
                    'channel': channel_username,
                    'message_id': message_id,
                    'marketplace': marketplace
                })
                
                # Сохраняем в базу как обработанное
                save_processed_message(message_id, clean_username, clean_text, marketplace)
                new_messages_count += 1
                
                # Выводим прогресс
                if new_messages_count % 5 == 0:
                    print(f"   📨 Новых сообщений: {new_messages_count}...")
            
            print(f"✅ {channel_username}: {new_messages_count} новых, {duplicate_count} дубликатов")
            
            # Показываем статистику по маркетплейсам
            if messages_data:
                marketplace_stats = {}
                for msg in messages_data:
                    mp = msg['marketplace']
                    marketplace_stats[mp] = marketplace_stats.get(mp, 0) + 1
                
                print(f"   📊 Распределение: {marketplace_stats}")
            
            return messages_data
            
        except FloodWait as e:
            print(f"⏳ Ожидание {e.value} секунд...")
            await asyncio.sleep(e.value)
            return await self.parse_channel_messages(channel_username, limit, is_source)
        except Exception as e:
            print(f"❌ Ошибка парсинга {channel_username}: {e}")
            return []
    
    def clean_message_text(self, text: str) -> str:
        """Очищает текст сообщения"""
        import re
        
        # Удаляем URL
        text = re.sub(r'http\S+', '', text)
        # Удаляем специальные символы, но сохраняем кириллицу и пунктуацию
        text = re.sub(r'[^\w\s\.\!\?,:;-а-яА-Я]', '', text)
        # Удаляем множественные пробелы
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    async def parse_all_channels(self):
        """Парсит все каналы с разными лимитами"""
        try:
            await self.initialize()
            
            print("=" * 50)
            print("🚀 УМНЫЙ ПАРСИНГ С РАЗДЕЛЕНИЕМ ПО МАРКЕТПЛЕЙСАМ")
            print("=" * 50)
            
            all_data = {'sources': [], 'discussions': []}
            marketplace_counts = {'total': 0, 'OZON': 0, 'WB': 0, 'other': 0}
            
            # Парсим основные каналы с большим лимитом
            print(f"\n📋 ОСНОВНЫЕ КАНАЛЫ (лимит: {config.SOURCE_LIMIT}):")
            for channel in config.SOURCE_CHANNELS:
                messages = await self.parse_channel_messages(channel, config.SOURCE_LIMIT, is_source=True)
                all_data['sources'].extend(messages)
                
                # Считаем статистику
                for msg in messages:
                    marketplace_counts['total'] += 1
                    marketplace_counts[msg['marketplace']] = marketplace_counts.get(msg['marketplace'], 0) + 1
            
            # Парсим доп. каналы с меньшим лимитом
            print(f"\n💬 ДОП. КАНАЛЫ (лимит: {config.DISCUSSION_LIMIT}):")
            for channel in config.DISCUSSION_CHANNELS:
                messages = await self.parse_channel_messages(channel, config.DISCUSSION_LIMIT, is_source=False)
                all_data['discussions'].extend(messages)
                
                # Считаем статистику
                for msg in messages:
                    marketplace_counts['total'] += 1
                    marketplace_counts[msg['marketplace']] = marketplace_counts.get(msg['marketplace'], 0) + 1
            
            # Обновляем статистику
            update_stats(marketplace_counts)
            
            # Выводим итоговую статистику
            print(f"\n📈 ИТОГИ ПАРСИНГА:")
            print(f"   📊 Всего новых сообщений: {marketplace_counts['total']}")
            print(f"   🟠 OZON: {marketplace_counts['OZON']}")
            print(f"   🔵 WB: {marketplace_counts['WB']}")
            print(f"   ⚪ Другие: {marketplace_counts['other']}")
            print(f"   📋 Основные: {len(all_data['sources'])}")
            print(f"   💬 Обсуждения: {len(all_data['discussions'])}")
            
            return all_data
            
        except Exception as e:
            print(f"❌ Критическая ошибка парсинга: {e}")
            return {'sources': [], 'discussions': []}
        finally:
            await self.shutdown()