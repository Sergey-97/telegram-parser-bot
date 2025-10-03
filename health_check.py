from flask import Flask, jsonify
import threading

app = Flask(__name__)

@app.route('/')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Telegram Parser Bot',
        'message': 'Bot is running successfully!'
    })

@app.route('/status')
def status():
    return jsonify({
        'status': 'running',
        'bot': 'active'
    })

def run_health_check():
    app.run(host='0.0.0.0', port=10000, debug=False)

def start_health_check():
    health_thread = threading.Thread(target=run_health_check)
    health_thread.daemon = True
    health_thread.start()
    return health_thread