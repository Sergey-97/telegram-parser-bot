# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Hugging Face
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN', '')

# Каналы
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL', '@mar_factor')
SOURCE_CHANNELS = [ch.strip() for ch in os.getenv('SOURCE_CHANNELS', '').split(',') if ch.strip()]
DISCUSSION_CHANNELS = [ch.strip() for ch in os.getenv('DISCUSSION_CHANNELS', '').split(',') if ch.strip()]

# Настройки парсинга
SOURCE_LIMIT = int(os.getenv('SOURCE_LIMIT', 15))  # Количество постов из основных каналов
DISCUSSION_LIMIT = int(os.getenv('DISCUSSION_LIMIT', 10))  # Количество постов из доп каналов
PARSE_INTERVAL_DAYS = int(os.getenv('PARSE_INTERVAL_DAYS', 1))

# Настройки приложения
PUBLISH_TIME = os.getenv('PUBLISH_TIME', '10:00')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot_database.db')

# Ключевые слова для определения маркетплейсов
MARKETPLACE_KEYWORDS = {
    'OZON': ['ozon', 'озон', 'озона', 'озоне'],
    'WB': ['wildberries', 'вб', 'wb', 'вайлдберриз', 'wildberry']
}

def validate_config():
    required = ['API_ID', 'API_HASH', 'BOT_TOKEN']
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        print(f"❌ Отсутствуют: {', '.join(missing)}")
        return False
    
    print(f"✅ Конфигурация загружена")
    print(f"   Основные каналы: {len(SOURCE_CHANNELS)} (лимит: {SOURCE_LIMIT})")
    print(f"   Доп. каналы: {len(DISCUSSION_CHANNELS)} (лимит: {DISCUSSION_LIMIT})")
    return True

if __name__ == "__main__":
    validate_config()