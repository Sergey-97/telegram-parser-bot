from database import init_db
from nlp_processor import NLPProcessor

print("Инициализация базы данных...")
init_db()

print("Загрузка NLP моделей...")
nlp = NLPProcessor()
nlp.load_models()

print("Бот готов к работе!")