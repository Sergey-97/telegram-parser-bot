# check_env_token.py
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Проверка загрузки токена из .env:")
print(f"HUGGINGFACE_TOKEN: {os.getenv('HUGGINGFACE_TOKEN')}")

if os.getenv('HUGGINGFACE_TOKEN'):
    print("✅ Токен загружен из .env!")
    print(f"Длина токена: {len(os.getenv('HUGGINGFACE_TOKEN'))} символов")
else:
    print("❌ Токен НЕ загружен из .env!")
    print("💡 Проверьте что в .env есть строка: HUGGINGFACE_TOKEN=ваш_токен")