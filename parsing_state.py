import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def init_parsing_state():
    """Инициализирует таблицу для отслеживания состояния парсинга"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parsing_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_url TEXT UNIQUE NOT NULL,
            last_message_id INTEGER DEFAULT 0,
            last_parsed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_parsed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ Таблица состояния парсинга инициализирована")

def is_first_run():
    """Проверяет, первый ли это запуск парсинга"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM parsing_state')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count == 0

def get_channel_state(channel_url):
    """Получает состояние парсинга для канала"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT last_message_id, total_parsed FROM parsing_state 
        WHERE channel_url = ?
    ''', (channel_url,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'last_message_id': result[0],
            'total_parsed': result[1],
            'is_first_run': False
        }
    else:
        return {
            'last_message_id': 0,
            'total_parsed': 0,
            'is_first_run': True
        }

def update_channel_state(channel_url, last_message_id, new_messages_count):
    """Обновляет состояние парсинга для канала"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO parsing_state 
        (channel_url, last_message_id, total_parsed, last_parsed_date)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ''', (channel_url, last_message_id, new_messages_count))
    
    conn.commit()
    conn.close()

def get_parsing_stats():
    """Получает общую статистику парсинга"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as channels, SUM(total_parsed) as total FROM parsing_state')
    result = cursor.fetchone()
    
    conn.close()
    
    return {
        'total_channels': result[0] or 0,
        'total_messages_parsed': result[1] or 0
    }