# bot_simple_http.py
import requests
import os
import time
from dotenv import load_dotenv
from ai_processor_final import AIProcessorFinal
from post_formatter import PostFormatter

load_dotenv()

class SimpleBot:
    def __init__(self):
        self.token = os.getenv('BOT_TOKEN')
        self.target_channel = os.getenv('TARGET_CHANNEL', '@mar_factor')
        self.ai_processor = AIProcessorFinal()
        self.post_formatter = PostFormatter()
    
    def check_channel_access(self):
        """Проверяет доступ к каналу"""
        url = f"https://api.telegram.org/bot{self.token}/getChat"
        payload = {
            'chat_id': self.target_channel
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                chat_info = response.json()
                print(f"✅ Канал найден: {chat_info['result']['title']}")
                return True
            else:
                print(f"❌ Ошибка доступа к каналу: {response.status_code}")
                print("💡 Решения:")
                print("1. Убедитесь что бот добавлен в канал как администратор")
                print("2. Проверьте правильность @username канала")
                print("3. Попробуйте использовать ID канала вместо @username")
                return False
        except Exception as e:
            print(f"❌ Ошибка проверки канала: {e}")
            return False
    
    def send_message(self, text: str):
        """Отправляет сообщение через HTTP API"""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            'chat_id': self.target_channel,
            'text': text,
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("✅ Сообщение отправлено")
                return True
            else:
                print(f"❌ Ошибка: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
            return False
    
    def run_manual_parse(self):
        """Ручной запуск парсинга и публикации"""
        print("🧠 Запуск AI-парсинга...")
        
        # Сначала проверяем доступ к каналу
        print("🔍 Проверяем доступ к каналу...")
        if not self.check_channel_access():
            print("❌ Не могу продолжить без доступа к каналу")
            return
        
        # Тестовые данные
        main_posts = [
            "Ozon запускает новую программу лояльности для продавцов. Теперь участники маркетплейса смогут получать дополнительные бонусы за объем продаж и положительные отзывы.",
            "Скидки до 50% на электронику в этом месяце! Успейте приобрести смартфоны, ноутбуки и планшеты по выгодным ценам. Акция действует до конца месяца."
        ]
        
        discussion_posts = [
            "Отличная новость про Ozon! Я как продавец очень доволен новыми условиями программы лояльности.",
            "Скидки на электронику просто супер! Уже присмотрел себе новый ноутбук по отличной цене."
        ]
        
        # AI-обработка
        structured_content = self.ai_processor.structure_content(main_posts, discussion_posts)
        
        # Форматирование поста
        final_post = self.post_formatter.format_structured_post(
            structured_content, 
            ['@ozon_adv', '@sklad1313']
        )
        
        print("📝 Сформированный пост:")
        print("=" * 50)
        print(final_post)
        print("=" * 50)
        
        # Публикация
        if input("Опубликовать этот пост? (y/n): ").lower() == 'y':
            success = self.send_message(final_post)
            if success:
                print("🎉 Пост успешно опубликован!")
            else:
                print("❌ Не удалось опубликовать пост")
        else:
            print("❌ Публикация отменена")

if __name__ == "__main__":
    bot = SimpleBot()
    bot.run_manual_parse()