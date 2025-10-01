from database import init_db, Session, Post, BotConfig

def setup_database():
    print("Инициализация базы данных...")
    init_db()
    
    # Создаем тестовую запись чтобы убедиться что все работает
    session = Session()
    try:
        test_post = Post(
            channel='@test',
            message_id=1,
            text='Тестовый пост для инициализации БД',
            processed=True
        )
        session.add(test_post)
        session.commit()
        print("База данных успешно инициализирована!")
    except Exception as e:
        print(f"Ошибка при инициализации БД: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    setup_database()