# database.py
import sqlite3
import logging
from datetime import datetime, timedelta
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
        # Таблица для отслеживания обработанных сообщений
        conn.execute('''
            CREATE TABLE IF NOT EXISTS processed_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                channel TEXT NOT NULL,
                text_hash TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                marketplace TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для статистики
        conn.execute('''
            CREATE TABLE IF NOT EXISTS parsing_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                total_messages INTEGER DEFAULT 0,
                ozon_messages INTEGER DEFAULT 0,
                wb_messages INTEGER DEFAULT 0,
                other_messages INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
    logger.info("✅ База данных инициализирована")

def is_message_processed(message_id: str, channel: str) -> bool:
    """Проверяет, было ли сообщение уже обработано"""
    with get_db_connection() as conn:
        cursor = conn.execute('''
            SELECT 1 FROM processed_messages 
            WHERE message_id = ? AND channel = ?
        ''', (message_id, channel))
        return cursor.fetchone() is not None

def save_processed_message(message_id: str, channel: str, text: str, marketplace: str = None):
    """Сохраняет информацию об обработанном сообщении"""
    import hashlib
    
    # Создаем хеш текста для дополнительной проверки
    text_hash = hashlib.md5(text.encode()).hexdigest()
    
    with get_db_connection() as conn:
        try:
            conn.execute('''
                INSERT OR IGNORE INTO processed_messages 
                (message_id, channel, text_hash, marketplace)
                VALUES (?, ?, ?, ?)
            ''', (message_id, channel, text_hash, marketplace))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка сохранения сообщения: {e}")
            return False

def get_today_stats():
    """Возвращает статистику за сегодня"""
    today = datetime.now().date()
    
    with get_db_connection() as conn:
        cursor = conn.execute('''
            SELECT * FROM parsing_stats WHERE date = ?
        ''', (today,))
        return cursor.fetchone()

def update_stats(marketplace_counts: dict):
    """Обновляет статистику парсинга"""
    today = datetime.now().date()
    
    with get_db_connection() as conn:
        # Получаем текущую статистику
        cursor = conn.execute('SELECT * FROM parsing_stats WHERE date = ?', (today,))
        existing = cursor.fetchone()
        
        if existing:
            # Обновляем существующую запись
            conn.execute('''
                UPDATE parsing_stats 
                SET total_messages = total_messages + ?,
                    ozon_messages = ozon_messages + ?,
                    wb_messages = wb_messages + ?,
                    other_messages = other_messages + ?
                WHERE date = ?
            ''', (
                marketplace_counts.get('total', 0),
                marketplace_counts.get('OZON', 0),
                marketplace_counts.get('WB', 0),
                marketplace_counts.get('other', 0),
                today
            ))
        else:
            # Создаем новую запись
            conn.execute('''
                INSERT INTO parsing_stats 
                (date, total_messages, ozon_messages, wb_messages, other_messages)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                today,
                marketplace_counts.get('total', 0),
                marketplace_counts.get('OZON', 0),
                marketplace_counts.get('WB', 0),
                marketplace_counts.get('other', 0)
            ))
        
        conn.commit()

def cleanup_old_messages(days=30):
    """Удаляет старые записи"""
    cutoff_date = (datetime.now() - timedelta(days=days)).date()
    
    with get_db_connection() as conn:
        conn.execute('DELETE FROM processed_messages WHERE created_at < ?', (cutoff_date,))
        conn.commit()
        logger.info(f"✅ Удалены записи старше {days} дней")

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