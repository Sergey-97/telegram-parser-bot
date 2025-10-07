# check_bot_simple.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def check_bot_token_simple():
    """Простая проверка токена бота через Telegram API"""
    token = os.getenv('BOT_TOKEN')
    
    if not token:
        print("❌ Токен бота не найден в .env")
        print("💡 Добавьте BOT_TOKEN=ваш_токен в файл .env")
        return False
    
    print(f"🔐 Проверяем токен: {token[:15]}...")
    
    try:
        # Прямой запрос к Telegram Bot API
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                bot_info = data['result']
                print(f"✅ Токен рабочий! Бот: {bot_info['first_name']} (@{bot_info['username']})")
                return True
            else:
                print(f"❌ Ошибка API: {data.get('description')}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            if response.status_code == 401:
                print("💡 Токен неверный или истек срок действия")
                print("Получите новый токен через @BotFather:")
                print("/mybots → выберите бота → API Token → Revoke → Generate new token")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки: {e}")
        return False

if __name__ == "__main__":
    check_bot_token_simple()