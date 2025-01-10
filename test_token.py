# test_main.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, Base, UserDB
from init_db import init_db

# Настройка базы данных для тестов
DATABASE_URL = "sqlite:///./test_test.db"  # Используем отдельную БД для тестов


# Создание тестового клиента
@pytest.fixture
def test_client():
    # Создание базы данных
    engine = create_engine(DATABASE_URL)

    # Создание сессии
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    app.dependency_overrides[SessionLocal] = lambda: SessionLocal()
    Base.metadata.create_all(bind=engine)

    # Инициализация базы данных
    init_db(SessionLocal)

    with TestClient(app) as client:
        yield client

    # Удаление базы данных после тестов
    Base.metadata.drop_all(bind=engine)


# Тестирование корневого эндпоинта
def test_read_root(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert "Добро пожаловать в FastAPI!" in response.text

# Тестирование получения токена
def test_login(test_client):
    response = test_client.post("/token", data={"username": "employee", "wrongpassword": "password"})
    assert response.status_code == 422  # 422 - ошибка со стороны сервера, при котором он понимает запрос,
    # но не может его выполнить

    response = test_client.post("/token", data={"username": "employee", "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()

# Тестирование получения бонусов
def test_read_bonuses(test_client):
    # Получаем токен
    response = test_client.post("/token", data={"username": "employee", "password": "password"})
    token = response.json()["access_token"]

    # Получаем бонусы
    response = test_client.get("/bonuses/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "employee"
    assert response.json()["level"] == "gold"
    assert response.json()["cashback"] == 5.0
    assert response.json()["spend"] == 100.0
