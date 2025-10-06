import os
from dotenv import load_dotenv

# ✅ ОБЯЗАТЕЛЬНО загружаем .env в начале файла
load_dotenv()

class AIProcessor:
    def __init__(self):
        self.api_urls = {
            'summarize': 'https://api-inference.huggingface.co/models/facebook/bart-large-cnn',
            'sentiment': 'https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest',
        }
        # ✅ Берем токен ИЗ .env
        self.headers = {'Authorization': f'Bearer {os.getenv("HUGGINGFACE_TOKEN")}'}