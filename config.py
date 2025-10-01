import os
from datetime import timedelta
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (для локальной разработки)
load_dotenv()

# Настройки Telegram API
API_ID = os.environ.get('API_ID', '')
API_HASH = os.environ.get('API_HASH', '')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')

# Проверяем обязательные переменные
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("Не установлены обязательные переменные окружения: API_ID, API_HASH, BOT_TOKEN")

# Настройки парсинга
PARSE_INTERVAL_DAYS = int(os.environ.get('PARSE_INTERVAL_DAYS', '7'))
PUBLISH_TIME = os.environ.get('PUBLISH_TIME', "10:00")

# Списки каналов
SOURCE_CHANNELS = [ch.strip() for ch in os.environ.get('SOURCE_CHANNELS', '@news1,@news2').split(',') if ch.strip()]
DISCUSSION_CHANNELS = [ch.strip() for ch in os.environ.get('DISCUSSION_CHANNELS', '@discussion1,@discussion2').split(',') if ch.strip()]
TARGET_CHANNEL = os.environ.get('TARGET_CHANNEL', '@your_target_channel')

# Настройки NLP
SUMMARY_MODEL = "IlyaGusev/mbart_ru_sum_gazeta"
COMMENT_MODEL = "cointegrated/rubert-tiny2"

# Настройки базы данных
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///bot_database.db')

# Оптимизации для бесплатного плана
MAX_POSTS_PER_CHANNEL = 50
PROCESSING_BATCH_SIZE = 5
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Выводим информацию о конфигурации (без чувствительных данных)
print(f"Конфигурация загружена: {len(SOURCE_CHANNELS)} исходных каналов, {len(DISCUSSION_CHANNELS)} каналов обсуждений")