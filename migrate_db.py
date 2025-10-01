from database import init_db, Session, Post
from datetime import datetime

def setup_database():
    print("🔄 Проверяем инициализацию базы данных...")
    
    # Просто вызываем init_db, который уже создает таблицы
    try:
        session = Session()
        
        # Проверяем соединение
        test_post = session.query(Post).first()
        print("✅ База данных подключена успешно!")
        
        # Создаем тестовый пост если нет постов
        if not test_post:
            test_post = Post(
                channel='@test',
                message_id=1,
                text='Тестовый пост для инициализации БД',
                date=datetime.now(),
                processed=True
            )
            session.add(test_post)
            session.commit()
            print("✅ Тестовые данные добавлены")
        
        # Статистика
        total = session.query(Post).count()
        processed = session.query(Post).filter_by(processed=True).count()
        print(f"📊 Всего постов: {total}, обработано: {processed}")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Ошибка при проверке БД: {e}")

if __name__ == '__main__':
    setup_database()