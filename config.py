import os
from dotenv import load_dotenv

load_dotenv()

# API ключи
HUGGINGFACE_TOKEN = os.getenv('HUGGINGFACE_TOKEN', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')

# Настройки Telegram API
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')

# Целевой канал для публикации
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL', '@mar_factor')

# Каналы для парсинга
SOURCE_CHANNELS = [
    "https://t.me/ozonmarketplace",
    "https://t.me/wbsellerofficial", 
    "https://t.me/ozon_adv",
    "https://t.me/sklad1313",
    "https://t.me/sellmonitor_com",
    "https://t.me/redmilliard",
    "https://t.me/marketplace_hogwarts",
    "https://t.me/mpgo_ru",
    "https://t.me/ProdaemWB",
    "https://t.me/ProdaemOZON"
]

# Настройки парсинга
MAIN_CHANNELS_LIMIT = 20
DISCUSSION_CHANNELS_LIMIT = 10