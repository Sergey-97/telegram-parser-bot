from flask import Flask, jsonify
import threading
import logging
from datetime import datetime

app = Flask(__name__)

# Простая страница для health check
@app.route('/')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Telegram Parser Bot',
        'timestamp': datetime.now().isoformat(),
        'message': 'Bot is running successfully!'
    })

@app.route('/status')
def status():
    """Расширенная информация о статусе"""
    try:
        from database import Session, Post
        session = Session()
        
        total_posts = session.query(Post).count()
        processed_posts = session.query(Post).filter_by(processed=True).count()
        new_posts = session.query(Post).filter_by(processed=False).count()
        
        session.close()
        
        return jsonify({
            'status': 'running',
            'database': 'connected',
            'posts_total': total_posts,
            'posts_processed': processed_posts,
            'posts_new': new_posts,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

def run_health_check():
    """Запускает Flask сервер для health check"""
    try:
        print("🏥 Health check сервер запускается на порту 5000...")
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        print(f"❌ Ошибка при запуске health check сервера: {e}")

def start_health_check():
    """Запускает health check в отдельном потоке"""
    health_thread = threading.Thread(target=run_health_check)
    health_thread.daemon = True
    health_thread.start()
    return health_thread