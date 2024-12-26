from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, UserDB  # Импортируйте ваши модели из файла models.py

# Настройка базы данных
DATABASE_URL = "sqlite:///./test.db"  # Убедитесь, что это совпадает с вашим приложением FastAPI
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Функция для инициализации базы данных
def init_db():
    # Создание всех таблиц
    Base.metadata.create_all(bind=engine)

    # Создание сессии
    db = SessionLocal()

    # Создание пользователей
    users = [
        UserDB(username="employee", hashed_password="fakehashedpassword", level="gold", cashback=5.0, spend=100.0),
        UserDB(username="client", hashed_password="fakehashedpassword123", level="silver", cashback=3.0, spend=50.0),
        UserDB(username="admin", hashed_password="fakehashedadmin", level="platinum", cashback=10.0, spend=200.0),
    ]

    # Добавление пользователей в базу данных
    db.add_all(users)
    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
