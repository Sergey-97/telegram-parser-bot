import os
import logging
from flask import Flask

# Базовая настройка
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>🤖 Telegram Parser Bot</h1>
    <p>Сервер работает! Базовая версия.</p>
    <ul>
        <li><a href="/health">/health</a> - Проверка</li>
        <li><a href="/test">/test</a> - Тест</li>
    </ul>
    """

@app.route('/health')
def health():
    return "✅ OK"

@app.route('/test')
def test():
    return "🧪 Тест работает"

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)