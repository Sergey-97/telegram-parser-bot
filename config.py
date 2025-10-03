import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Проверяем обязательные переменные
required_vars = ['API_ID', 'API_HASH', 'BOT_TOKEN']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print(f"❌ ВНИМАНИЕ: Не установлены обязательные переменные окружения: {', '.join(missing_vars)}")
else:
    print("✅ Все обязательные переменные окружения установлены")

# Telegram API настройки
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')

# Настройки каналов
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL', '').strip()
SOURCE_CHANNELS = [channel.strip() for channel in os.getenv('SOURCE_CHANNELS', '').split(',') if channel.strip()]
DISCUSSION_CHANNELS = [channel.strip() for channel in os.getenv('DISCUSSION_CHANNELS', '').split(',') if channel.strip()]

# Настройки приложения
PARSE_INTERVAL_DAYS = int(os.getenv('PARSE_INTERVAL_DAYS', 7))
PUBLISH_TIME = os.getenv('PUBLISH_TIME', '10:00')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# База данных
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot_database.db')

# Выводим информацию о загруженной конфигурации
print(f"✅ Конфигурация загружена: {len(SOURCE_CHANNELS)} исходных каналов, {len(DISCUSSION_CHANNELS)} каналов обсуждений")
print(f"🎯 Целевой канал: {TARGET_CHANNEL}")