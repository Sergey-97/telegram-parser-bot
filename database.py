import sqlite3
import logging
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

def get_db_connection():
    """Создает соединение с базой данных"""
    conn = sqlite3.connect('bot_database.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Инициализирует базу данных"""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS parsed_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER NOT NULL,
                channel TEXT NOT NULL,
                text TEXT NOT NULL,
                date TIMESTAMP NOT NULL,
                published BOOLEAN DEFAULT FALSE,
                published_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
    logger.info("✅ База данных инициализирована")

def save_message(message_id: int, channel: str, text: str, date: datetime, published: bool = False):
    """Сохраняет сообщение в базу данных"""
    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR IGNORE INTO parsed_messages 
            (message_id, channel, text, date, published, published_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (message_id, channel, text, date, published, datetime.now() if published else None))
        conn.commit()

def get_last_parsed_date() -> datetime:
    """Возвращает дату последнего парсинга"""
    with get_db_connection() as conn:
        cursor = conn.execute('''
            SELECT MAX(date) as last_date FROM parsed_messages
        ''')
        result = cursor.fetchone()
        return datetime.fromisoformat(result['last_date']) if result['last_date'] else None

def is_message_processed(message_id: int, channel: str) -> bool:
    """Проверяет, было ли сообщение уже обработано"""
    with get_db_connection() as conn:
        cursor = conn.execute('''
            SELECT 1 FROM parsed_messages 
            WHERE message_id = ? AND channel = ?
        ''', (message_id, channel))
        return cursor.fetchone() is not None

def add_keyword(keyword: str):
    """Добавляет ключевое слово в базу данных"""
    with get_db_connection() as conn:
        conn.execute('''
            INSERT OR IGNORE INTO keywords (keyword) VALUES (?)
        ''', (keyword,))
        conn.commit()

def get_keywords() -> list:
    """Возвращает список ключевых слов"""
    with get_db_connection() as conn:
        cursor = conn.execute('SELECT keyword FROM keywords')
        return [row['keyword'] for row in cursor.fetchall()]

@contextmanager
def db_transaction():
    """Контекстный менеджер для транзакций"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()