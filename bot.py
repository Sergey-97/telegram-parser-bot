# bot.py
import asyncio
import requests
import os
from dotenv import load_dotenv
from parser import Parser
from ai_processor import AIProcessor
from post_formatter import PostFormatter
import config

load_dotenv()

class Bot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN')
        self.target_channel = os.getenv('TARGET_CHANNEL', '@mar_factor')
        self.parser = Parser()
        self.ai_processor = AIProcessor()
        self.post_formatter = PostFormatter()
    
    def test_bot_access(self):
        """Проверяет доступ бота к целевому каналу"""
        url = f"https://api.telegram.org/bot{self.token}/getChat"
        response = requests.post(url, json={'chat_id': self.target_channel}, timeout=10)
        
        if response.status_code == 200:
            chat_info = response.json()['result']
            print(f"✅ Целевой канал: {chat_info.get('title', 'N/A')}")
            return True
        print(f"❌ Ошибка доступа: {response.status_code}")
        return False
    
    def publish_post(self, text: str):
        """Публикует пост в канал"""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            'chat_id': self.target_channel,
            'text': text,
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Ошибка API: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return False
    
    def create_fallback_post(self):
        """Создает резервный пост если парсинг не удался"""
        print("🔄 Создаю резервный пост...")
        
        fallback_news = [
            "Ozon запускает осеннюю программу лояльности для продавцов с повышенными бонусами за объем продаж и качество обслуживания.",
            "Сезонные скидки до 50% на электронику и бытовую технику. В акции участвуют смартфоны, ноутбуки, планшеты и умные устройства.",
            "Wildberries расширяет логистическую сеть: добавлены новые пункты выдачи в Москве, Санкт-Петербурге и других крупных городах."
        ]
        
        fallback_comments = [
            "Отличные новости от Ozon! Новые условия программы лояльности очень мотивируют развивать бизнес на маркетплейсе.",
            "Скидки на технику просто супер! Уже присмотрел новый MacBook по выгодной цене. Отличное время для покупок!",
            "Удобно, что Wildberries расширяет сеть пунктов выдачи. Теперь получать заказы стало еще проще и ближе к дому."
        ]
        
        structured_content = self.ai_processor.structure_content(fallback_news, fallback_comments)
        post = self.post_formatter.format_structured_post(structured_content, config.SOURCE_CHANNELS)
        
        return post
    
    async def create_post_with_real_parsing(self):
        """Создает пост на основе реального парсинга"""
        print("🔍 Запускаю реальный парсинг каналов...")
        
        # Парсим каналы
        parsed_data = await self.parser.parse_all_channels()
        source_texts = [msg['text'] for msg in parsed_data['sources']]
        discussion_texts = [msg['text'] for msg in parsed_data['discussions']]
        
        print(f"\n📥 РЕЗУЛЬТАТЫ ПАРСИНГА:")
        print(f"   Основные каналы: {len(source_texts)} сообщений")
        print(f"   Обсуждения: {len(discussion_texts)} сообщений")
        
        # Если парсинг не удался, используем резервный контент
        if len(source_texts) < 2:
            print("⚠️  Мало данных от парсинга, использую резервный контент")
            return self.create_fallback_post()
        
        print("🧠 Обрабатываю реальный контент...")
        structured_content = self.ai_processor.structure_content(source_texts, discussion_texts)
        
        # Добавляем метку что это реальные данные
        if len(source_texts) > 0:
            structured_content['main_topic'] = f"РЕАЛЬНЫЕ ДАННЫЕ | {structured_content['main_topic']}"
        
        post = self.post_formatter.format_structured_post(
            structured_content, 
            config.SOURCE_CHANNELS + config.DISCUSSION_CHANNELS
        )
        
        return post
    
    async def run(self):
        """Основной запуск бота"""
        print("=" * 60)
        print("🚀 TELEGRAM AI ПАРСЕР БОТ - РЕАЛЬНЫЙ ПАРСИНГ")
        print("=" * 60)
        
        # Проверка доступа бота
        if not self.test_bot_access():
            print("❌ Не могу продолжить без доступа к целевому каналу")
            return
        
        # Создаем пост
        post = await self.create_post_with_real_parsing()
        
        if not post:
            print("❌ Не удалось создать пост")
            return
        
        # Показываем пост
        print("\n📝 СОЗДАННЫЙ ПОСТ:")
        print("=" * 60)
        print(post)
        print("=" * 60)
        
        # Подтверждение публикации
        choice = input("\n📤 Опубликовать этот пост? (y/n): ").strip().lower()
        if choice == 'y':
            print("⏳ Публикую...")
            if self.publish_post(post):
                print("\n🎉 ПОСТ УСПЕШНО ОПУБЛИКОВАН!")
                print(f"👀 Посмотреть: https://t.me/mar_factor")
                
                print("\n📊 СТАТИСТИКА:")
                print(f"   📏 Длина поста: {len(post)} символов")
                print(f"   📄 Строк: {post.count(chr(10)) + 1}")
                print(f"   🔍 Каналов отслеживается: {len(config.SOURCE_CHANNELS + config.DISCUSSION_CHANNELS)}")
            else:
                print("❌ Ошибка публикации поста")
        else:
            print("❌ Публикация отменена")

if __name__ == "__main__":
    bot = Bot()
    asyncio.run(bot.run())