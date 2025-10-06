# test_token_access.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_token_access():
    token = os.getenv('HUGGINGFACE_TOKEN')
    headers = {'Authorization': f'Bearer {token}'}
    
    print("🔐 Тестируем доступ токена...")
    
    try:
        # Проверяем базовую информацию
        response = requests.get('https://huggingface.co/api/whoami', headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Токен валидный! Пользователь: {user_info.get('name')}")
            print(f"📧 Email: {user_info.get('email')}")
            return True
        elif response.status_code == 401:
            print("❌ Ошибка 401: Неавторизованный доступ")
            print("💡 Возможные причины:")
            print("   - Токен неверный")
            print("   - Токен отозван")
            print("   - Токен неактивен")
            return False
        elif response.status_code == 403:
            print("❌ Ошибка 403: Доступ запрещен")
            print("💡 У токена недостаточно прав")
            return False
        else:
            print(f"❌ Неизвестная ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    test_token_access()