from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def health_check():
    return {
        'status': 'healthy',
        'service': 'Telegram Parser Bot',
        'message': 'Bot is running successfully!'
    }

@app.route('/status')
def status():
    return {
        'status': 'running',
        'bot': 'active'
    }

def run_health_check():
    app.run(host='0.0.0.0', port=10000, debug=False)

# Запускаем health check в отдельном потоке
health_thread = threading.Thread(target=run_health_check)
health_thread.daemon = True
health_thread.start()