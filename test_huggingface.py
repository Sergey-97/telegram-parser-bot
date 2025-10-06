# test_huggingface.py
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

async def test_huggingface_token():
    """Тестирует корректность токена Hugging Face"""
    
    token = os.getenv('HUGGINGFACE_TOKEN')
    if not token:
        print("❌ Токен не найден в .env файле")
        return False
    
    headers = {'Authorization': f'Bearer {token}'}
    api_url = 'https://api-inference.huggingface.co/models/facebook/bart-large-cnn'
    
    try:
        async with aiohttp.ClientSession() as session:
            # Простой запрос для проверки токена
            async with session.get('https://huggingface.co/api/whoami', headers=headers) as response:
                if response.status == 200:
                    user_info = await response.json()
                    print(f"✅ Токен работает! Пользователь: {user_info.get('name')}")
                    return True
                else:
                    print(f"❌ Ошибка токена: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_huggingface_token())