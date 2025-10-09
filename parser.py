import asyncio
from pyrogram import Client
from database import save_message, message_exists
from ai_processor import AIProcessor
from config import SOURCE_CHANNELS, MAIN_CHANNELS_LIMIT, DISCUSSION_CHANNELS_LIMIT

class TelegramParser:
    def __init__(self, client: Client):
        self.client = client
        self.ai_processor = AIProcessor()
        
    async def parse_channel(self, channel_url, limit=20):
        """Парсит указанный канал и возвращает новые сообщения"""
        try:
            print(f"🔍 Парсим {channel_url} (лимит: {limit})...")
            
            # Извлекаем username/id канала из URL
            if channel_url.startswith('https://t.me/'):
                channel_identifier = channel_url.replace('https://t.me/', '')
            else:
                channel_identifier = channel_url
                
            messages = []
            new_messages_count = 0
            duplicate_count = 0
            
            async for message in self.client.get_chat_history(channel_identifier, limit=limit):
                if message.text:
                    message_text = message.text
                    
                    # Проверяем, есть ли уже такое сообщение в базе
                    if not message_exists(message_text, channel_url):
                        # Определяем маркетплейс
                        marketplace = self.ai_processor.analyze_marketplace(message_text, channel_url)
                        
                        # Сохраняем в базу
                        save_message(message_text, channel_url, marketplace)
                        messages.append(message_text)
                        new_messages_count += 1
                    else:
                        duplicate_count += 1
            
            # Статистика по маркетплейсам для новых сообщений
            marketplace_stats = {}
            if new_messages_count > 0:
                for msg in messages:
                    marketplace = self.ai_processor.analyze_marketplace(msg)
                    marketplace_stats[marketplace] = marketplace_stats.get(marketplace, 0) + 1
                
                print(f"✅ {channel_url}: {new_messages_count} новых, {duplicate_count} дубликатов")
                if marketplace_stats:
                    print(f"   📊 Распределение: {marketplace_stats}")
            else:
                print(f"✅ {channel_url}: {new_messages_count} новых, {duplicate_count} дубликатов")
            
            return {
                'channel': channel_url,
                'new_messages': new_messages_count,
                'duplicates': duplicate_count,
                'messages': messages,
                'marketplace_stats': marketplace_stats
            }
            
        except Exception as e:
            print(f"❌ Ошибка парсинга {channel_url}: {e}")
            return {
                'channel': channel_url,
                'new_messages': 0,
                'duplicates': 0,
                'messages': [],
                'marketplace_stats': {},
                'error': str(e)
            }

    async def parse_all_channels(self):
        """Парсит все каналы из конфигурации"""
        print("📋 ОСНОВНЫЕ КАНАЛЫ (лимит: {}):".format(MAIN_CHANNELS_LIMIT))
        
        results = []
        total_new_messages = 0
        total_duplicates = 0
        marketplace_totals = {'OZON': 0, 'WB': 0, 'YANDEX': 0, 'OTHER': 0}
        
        # Основные каналы (первые 3)
        main_channels = SOURCE_CHANNELS[:3]
        for channel in main_channels:
            result = await self.parse_channel(channel, MAIN_CHANNELS_LIMIT)
            result['type'] = 'main'
            results.append(result)
            total_new_messages += result['new_messages']
            total_duplicates += result['duplicates']
            
            # Суммируем статистику по маркетплейсам
            for marketplace, count in result['marketplace_stats'].items():
                marketplace_totals[marketplace] += count
        
        print("\n💬 ДОП. КАНАЛЫ (лимит: {}):".format(DISCUSSION_CHANNELS_LIMIT))
        
        # Дополнительные каналы (остальные)
        discussion_channels = SOURCE_CHANNELS[3:]
        for channel in discussion_channels:
            result = await self.parse_channel(channel, DISCUSSION_CHANNELS_LIMIT)
            result['type'] = 'discussion'
            results.append(result)
            total_new_messages += result['new_messages']
            total_duplicates += result['duplicates']
            
            # Суммируем статистику по маркетплейсам
            for marketplace, count in result['marketplace_stats'].items():
                marketplace_totals[marketplace] += count
        
        # Выводим итоги
        print("\n📈 ИТОГИ ПАРСИНГА:")
        print(f"   📊 Всего новых сообщений: {total_new_messages}")
        print(f"   🟠 OZON: {marketplace_totals['OZON']}")
        print(f"   🔵 WB: {marketplace_totals['WB']}")
        print(f"   🟡 YANDEX: {marketplace_totals['YANDEX']}")
        print(f"   ⚪ Другие: {marketplace_totals['OTHER']}")
        
        main_messages = sum(r['new_messages'] for r in results if r['type'] == 'main')
        discussion_messages = sum(r['new_messages'] for r in results if r['type'] == 'discussion')
        print(f"   📋 Основные: {main_messages}")
        print(f"   💬 Обсуждения: {discussion_messages}")
        
        return {
            'results': results,
            'total_new_messages': total_new_messages,
            'total_duplicates': total_duplicates,
            'marketplace_totals': marketplace_totals
        }