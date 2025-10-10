import os
from dotenv import load_dotenv

load_dotenv()

# Базовые настройки
API_ID = int(os.getenv('API_ID', 0))
API_HASH = os.getenv('API_HASH', '')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL', '@mar_factor')

SOURCE_CHANNELS = [
    "https://t.me/ozonmarketplace",
    "https://t.me/wbsellerofficial", 
    "https://t.me/ozon_adv",
]