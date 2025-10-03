import os

# Настройки Telegram API
API_ID = os.environ.get('API_ID', '')
API_HASH = os.environ.get('API_HASH', '')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '')

# Проверяем обязательные переменные
if not all([API_ID, API_HASH, BOT_TOKEN]):
    print("❌ ВНИМАНИЕ: Не установлены обязательные переменные окружения: API_ID, API_HASH, BOT_TOKEN")

# Настройки парсинга
PARSE_INTERVAL_DAYS = int(os.environ.get('PARSE_INTERVAL_DAYS', '1'))  # 1 день для актуальности
MAX_POSTS_PER_CHANNEL = int(os.environ.get('MAX_POSTS_PER_CHANNEL', '5'))  # Последние 5 постов
PUBLISH_TIME = os.environ.get('PUBLISH_TIME', "10:00")

# Списки каналов
SOURCE_CHANNELS = [ch.strip() for ch in os.environ.get('SOURCE_CHANNELS', '@rian_ru,@tass_agency').split(',') if ch.strip()]
DISCUSSION_CHANNELS = [ch.strip() for ch in os.environ.get('DISCUSSION_CHANNELS', '@meduzalive').split(',') if ch.strip()]
TARGET_CHANNEL = os.environ.get('TARGET_CHANNEL', '@your_target_channel')

# Настройки базы данных
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///bot_database.db')

# Настройки NLP
SUMMARY_MODEL = "IlyaGusev/mbart_ru_sum_gazeta"
COMMENT_MODEL = "cointegrated/rubert-tiny2"

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

print(f"✅ Конфигурация загружена: {len(SOURCE_CHANNELS)} исходных каналов, {len(DISCUSSION_CHANNELS)} каналов обсуждений")