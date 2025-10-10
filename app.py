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
    <h1>🤖 Telegram Parser Bot - ИСПРАВЛЕННАЯ ВЕРСИЯ</h1>
    <p>Бот для парсинга реальных данных с Telegram каналов</p>
    
    <h3>🚀 Действия:</h3>
    <ul>
        <li><a href="/force-session">/force-session</a> - Принудительное создание сессии (СНАЧАЛА!)</li>
        <li><a href="/run-fixed">/run-fixed</a> - Запуск исправленного парсинга</li>
        <li><a href="/health">/health</a> - Проверка работы</li>
        <li><a href="/debug">/debug</a> - Диагностика</li>
    </ul>
    
    <h3>📊 Каналы для парсинга:</h3>
    <ul>
        <li>@ozonmarketplace</li>
        <li>@wbsellerofficial</li>
        <li>@ozon_adv</li>
        <li>@sklad1313</li>
        <li>@sellmonitor_com</li>
        <li>@redmilliard</li>
        <li>@marketplace_hogwarts</li>
        <li>@mpgo_ru</li>
        <li>@ProdaemWB</li>
        <li>@ProdaemOZON</li>
    </ul>
    
    <p><strong>⚠️ Важно:</strong> Сначала запустите /force-session для создания пользовательской сессии!</p>
    """

@app.route('/health')
def health():
    return "✅ Сервер работает"

@app.route('/force-session')
def force_session():
    """Принудительное создание пользовательской сессии на Render"""
    try:
        # Создаем новый event loop для асинхронной операции
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Импортируем и запускаем создание сессии
        from force_user_session import force_create_session
        loop.run_until_complete(force_create_session())
        loop.close()
        
        return """
        <h2>✅ Сессия создана!</h2>
        <p>Пользовательская сессия успешно создана на Render.</p>
        <p><strong>Теперь запустите:</strong> <a href="/run-fixed">/run-fixed</a></p>
        <a href="/">← Назад</a>
        """
    except Exception as e:
        return f"""
        <h2>❌ Ошибка создания сессии</h2>
        <p><strong>Ошибка:</strong> {str(e)}</p>
        <p>Проверьте API_ID и API_HASH в настройках Render</p>
        <a href="/">← Назад</a>
        """

@app.route('/run-fixed')
def run_fixed():
    """Запуск исправленной версии с пользовательской сессией"""
    try:
        # Создаем новый event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Импортируем и запускаем исправленный бот
        from bot_runner_fixed import run_bot_fixed
        result = loop.run_until_complete(run_bot_fixed())
        loop.close()
        
        return result
    except Exception as e:
        return f"""
        <h2>❌ Ошибка запуска</h2>
        <p><strong>Ошибка:</strong> {str(e)}</p>
        <p>Возможно, сессия не создана. Сначала запустите <a href="/force-session">/force-session</a></p>
        <a href="/">← Назад</a>
        """

@app.route('/debug')
def debug():
    """Диагностика системы"""
    try:
        import os
        import sys
        
        # Собираем информацию о системе
        files = os.listdir('.')
        session_files = [f for f in files if f.endswith('.session')]
        python_version = sys.version
        
        info = f"""
        <h2>🔍 Диагностика системы</h2>
        
        <h3>📁 Файлы в проекте:</h3>
        <ul>
        {"".join([f"<li>{f}</li>" for f in files if any(f.endswith(ext) for ext in ['.py', '.session', '.db'])])}
        </ul>
        
        <h3>🔐 Файлы сессии:</h3>
        <ul>
        {"".join([f"<li>{f}</li>" for f in session_files])}
        </ul>
        
        <h3>🐍 Python информация:</h3>
        <pre>{python_version}</pre>
        
        <h3>🛠️ Проверка импортов:</h3>
        <ul>
        """
        
        # Проверяем ключевые импорты
        imports_to_check = [
            'database', 'ai_processor', 'post_formatter', 'config',
            'bot_runner_fixed', 'force_user_session'
        ]
        
        for import_name in imports_to_check:
            try:
                __import__(import_name)
                info += f"<li>✅ {import_name}</li>"
            except ImportError as e:
                info += f"<li>❌ {import_name}: {e}</li>"
        
        info += "</ul>"
        info += '<a href="/">← Назад</a>'
        
        return info
        
    except Exception as e:
        return f"❌ Ошибка диагностики: {str(e)}"

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)