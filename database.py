import sqlite3
import json
from datetime import datetime

def init_db():
    """Инициализирует базу данных"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    # Таблица для сообщений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_text TEXT NOT NULL,
            channel_url TEXT NOT NULL,
            marketplace TEXT,
            message_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица для постов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована")

def save_message(message_text, channel_url, marketplace='OTHER'):
    """Сохраняет сообщение в базу данных"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO messages (message_text, channel_url, marketplace)
        VALUES (?, ?, ?)
    ''', (message_text, channel_url, marketplace))
    
    conn.commit()
    conn.close()

def message_exists(message_text, channel_url):
    """Проверяет, существует ли сообщение уже в базе"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM messages 
        WHERE message_text = ? AND channel_url = ?
    ''', (message_text, channel_url))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0

def post_exists(post_content):
    """Проверяет, был ли уже отправлен такой пост за последние 24 часа"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM posts 
        WHERE post_content = ? AND created_at > datetime('now', '-1 day')
    ''', (post_content,))
    
    count = cursor.fetchone()[0]
    conn.close()
    
    return count > 0

def get_last_messages(limit=10):
    """Получает последние сообщения из базы данных"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT message_text, channel_url, marketplace, created_at 
        FROM messages 
        ORDER BY created_at DESC 
        LIMIT ?
    ''', (limit,))
    
    messages = []
    for row in cursor.fetchall():
        messages.append({
            'text': row[0],
            'channel': row[1],
            'marketplace': row[2],
            'date': row[3]
        })
    
    conn.close()
    return messages

def save_post(post_content):
    """Сохраняет созданный пост в базу данных"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO posts (post_content)
        VALUES (?)
    ''', (post_content,))
    
    conn.commit()
    conn.close()