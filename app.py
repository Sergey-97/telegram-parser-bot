import os
import asyncio
import logging
from flask import Flask

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Инициализация базы данных
try:
    from database import init_db
    init_db()
    logger.info("✅ База данных инициализирована")
except Exception as e:
    logger.error(f"❌ Ошибка БД: {e}")

@app.route('/')
def home():
    return """
    <h1>🤖 Telegram Parser Bot</h1>
    <p>Бот для автоматической публикации аналитики маркетплейсов</p>
    
    <h3>🚀 Действия:</h3>
    <ul>
        <li><a href="/health">/health</a> - Проверка работы</li>
        <li><a href="/test-ai">/test-ai</a> - Тест AI обработки</li>
        <li><a href="/test-db">/test-db</a> - Тест базы данных</li>
        <li><a href="/create-post">/create-post</a> - Создать тестовый пост</li>
    </ul>
    
    <p><strong>Статус:</strong> ✅ Базовая функциональность работает</p>
    """

@app.route('/health')
def health():
    return "✅ Сервер работает"

@app.route('/test-ai')
def test_ai():
    """Тест AI обработки"""
    try:
        from ai_processor import AIProcessor
        from post_formatter import PostFormatter
        
        ai = AIProcessor()
        formatter = PostFormatter()
        
        # Тестовые сообщения
        test_messages = [
            "OZON запускает новую систему доставки",
            "WB обновляет правила возвратов",
            "Яндекс Маркет представляет новые инструменты"
        ]
        
        # Обработка AI
        structured = ai.structure_content(test_messages, [])
        post = formatter.format_structured_post(structured)
        
        return f"""
        <h2>🧪 Тест AI обработки</h2>
        <p><strong>Обработано сообщений:</strong> {len(test_messages)}</p>
        
        <h3>📝 Результат:</h3>
        <pre>{post}</pre>
        
        <a href="/">← Назад</a>
        """
    except Exception as e:
        return f"❌ Ошибка AI: {str(e)}"

@app.route('/test-db')
def test_db():
    """Тест базы данных"""
    try:
        from database import save_message, get_last_messages, save_post
        
        # Сохраняем тестовое сообщение
        save_message("Тестовое сообщение для проверки БД", "test_channel", "TEST")
        
        # Получаем сообщения
        messages = get_last_messages(5)
        
        # Сохраняем тестовый пост
        save_post("Тестовый пост в базе данных")
        
        return f"""
        <h2>🧪 Тест базы данных</h2>
        <p><strong>Сообщений в базе:</strong> {len(messages)}</p>
        
        <h3>📋 Последние сообщения:</h3>
        <ul>
        {"".join([f"<li>{msg['text'][:50]}...</li>" for msg in messages])}
        </ul>
        
        <a href="/">← Назад</a>
        """
    except Exception as e:
        return f"❌ Ошибка БД: {str(e)}"

@app.route('/create-post')
def create_post():
    """Создание тестового поста"""
    try:
        from ai_processor import AIProcessor
        from post_formatter import PostFormatter
        from database import save_post
        
        ai = AIProcessor()
        formatter = PostFormatter()
        
        # Тестовые данные
        test_data = [
            "OZON: новые правила модерации карточек товаров",
            "Wildberries увеличивает комиссию для электроники",
            "Яндекс Маркет запускает экспресс-доставку",
            "OZON улучшает логистические процессы",
            "WB вводит новые требования к карточкам"
        ]
        
        # Создаем пост
        structured = ai.structure_content(test_data, [])
        post_content = formatter.format_structured_post(structured)
        
        # Сохраняем в базу
        save_post(post_content)
        
        return f"""
        <h2>📝 Тестовый пост создан!</h2>
        <p><strong>Длина поста:</strong> {len(post_content)} символов</p>
        
        <h3>📄 Содержание:</h3>
        <pre>{post_content}</pre>
        
        <p><strong>✅ Пост сохранен в базу данных</strong></p>
        <a href="/">← Назад</a>
        """
    except Exception as e:
        return f"❌ Ошибка создания поста: {str(e)}"

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)