from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import re
from config import DATABASE_URL

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

def convert_database_url():
    """Конвертирует DATABASE_URL для совместимости с SQLAlchemy"""
    database_url = DATABASE_URL
    
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    return database_url

def init_db():
    """Инициализирует базу данных"""
    database_url = convert_database_url()
    
    if not database_url:
        database_url = 'sqlite:///bot_database.db'
    
    print(f"Подключаемся к базе данных: {database_url.split('://')[0]}")
    
    engine = create_engine(database_url)
    
    # Создаем таблицы
    try:
        Base.metadata.create_all(engine)
        print("Таблицы базы данных успешно созданы/проверены")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")
        # Если PostgreSQL недоступна, используем SQLite как запасной вариант
        if 'postgresql' in database_url:
            print("Переключаемся на SQLite...")
            database_url = 'sqlite:///bot_database.db'
            engine = create_engine(database_url)
            Base.metadata.create_all(engine)
    
    return sessionmaker(bind=engine)

# Создаем сессию базы данных
Session = init_db()