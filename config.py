import os
from datetime import timedelta

# Настройки Telegram API (будут установлены как environment variables в Render)
API_ID = os.environ.get('API_ID', 'your_api_id')
API_HASH = os.environ.get('API_HASH', 'your_api_hash')
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'your_bot_token')

# Настройки парсинга
PARSE_INTERVAL_DAYS = 7
PUBLISH_TIME = "10:00"

# Списки каналов (можно будет менять через environment variables)
SOURCE_CHANNELS = os.environ.get('SOURCE_CHANNELS', '@channel1,@channel2').split(',')
DISCUSSION_CHANNELS = os.environ.get('DISCUSSION_CHANNELS', '@discussion1,@discussion2').split(',')
TARGET_CHANNEL = os.environ.get('TARGET_CHANNEL', '@your_target_channel')

# Настройки NLP
SUMMARY_MODEL = "IlyaGusev/mbart_ru_sum_gazeta"
COMMENT_MODEL = "cointegrated/rubert-tiny2"

# Настройки базы данных для Render
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///bot_database.db')