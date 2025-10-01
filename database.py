from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
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

def init_db():
    # Для Render используем PostgreSQL если доступно, иначе SQLite
    if DATABASE_URL and DATABASE_URL.startswith('postgresql'):
        engine = create_engine(DATABASE_URL)
    else:
        engine = create_engine('sqlite:///bot_database.db')
    
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

# Создаем сессию базы данных
Session = init_db()