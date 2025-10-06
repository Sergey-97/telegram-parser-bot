# huggingface_official_test.py
from huggingface_hub import HfApi, login
import os
from dotenv import load_dotenv

load_dotenv()

def official_huggingface_test():
    token = os.getenv('HUGGINGFACE_TOKEN')
    
    if not token:
        print("❌ Токен не найден")
        return False
    
    try:
        print("🔐 Официальный тест Hugging Face...")
        
        # Пробуем войти через официальную библиотеку
        login(token=token)
        
        # Создаем клиент API
        api = HfApi()
        
        # Получаем информацию о пользователе
        user_info = api.whoami()
        print(f"✅ Успешный вход! Пользователь: {user_info['name']}")
        print(f"📧 Email: {user_info.get('email', 'N/A')}")
        
        # Пробуем получить информацию о модели
        model_info = api.model_info("facebook/bart-large-cnn")
        print(f"✅ Доступ к моделям: {model_info.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    official_huggingface_test()