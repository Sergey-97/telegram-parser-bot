from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import re

Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    channel = Column(String(255))
    message_id = Column(Integer)
    text = Column(Text)
    date = Column(DateTime)
    processed = Column(Boolean, default=False)
    processed_text = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

class BotConfig(Base):
    __tablename__ = 'config'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(255))
    value = Column(String(255))

def get_database_url():
    """Получает и корректирует URL базы данных"""
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///bot_database.db')
    
    # Исправляем для Render PostgreSQL
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    return database_url

def init_db():
    """Инициализирует базу данных"""
    database_url = get_database_url()
    
    print(f"🔗 Подключаемся к базе данных: {database_url.split('://')[0]}")
    
    try:
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        print("✅ Таблицы базы данных успешно созданы/проверены")
        return sessionmaker(bind=engine)
    except Exception as e:
        print(f"❌ Ошибка при подключении к основной БД: {e}")
        print("🔄 Пробуем использовать SQLite...")
        # Fallback на SQLite
        engine = create_engine('sqlite:///bot_database.db')
        Base.metadata.create_all(engine)
        return sessionmaker(bind=engine)

# Инициализируем сессию базы данных
Session = init_db()