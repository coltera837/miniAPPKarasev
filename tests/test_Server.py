import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from Server import app, get_db
from DBmodels import Base
from datetime import date, datetime

# Тестовая БД
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_create_phone_record_success(test_db):
    """Тест успешного создания записи"""
    data = {
        "data": {
            "number": "+79807060972",
            "currentDate": str(date.today()),
            "currentTime": datetime.now().strftime('%H:%M:%S'),
            "clickOrder": 1
        }
    }

    response = client.post("/addPhoneNumber", json=data)
    assert response.status_code == 200
    assert response.json()["number"] == "+79807060972"
    assert "id" in response.json()


def test_create_phone_record_validation_error(test_db):
    """Тест валидации номера телефона"""
    data = {
        "data": {
            "number": "invalid",
            "currentDate": str(date.today()),
            "currentTime": datetime.now().strftime('%H:%M:%S'),
            "clickOrder": 1
        }
    }

    response = client.post("/addPhoneNumber", json=data)
    assert response.status_code == 422

    response_data = response.json()
    assert "detail" in response_data
    assert len(response_data["detail"]) > 0
    assert any(error["type"] == "string_too_short" for error in response_data["detail"])


def test_get_phone_records_pagination(test_db):
    """Тест пагинации записей"""
    for i in range(1, 6):
        data = {
            "data": {
                "number": f"+7980706097{i}",
                "currentDate": str(date.today()),
                "currentTime": datetime.now().strftime('%H:%M:%S'),
                "clickOrder": i
            }
        }
        client.post("/addPhoneNumber", json=data)

    response = client.get("/NumberList?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 5
    assert data["limit"] == 2
    assert data["skip"] == 2
    assert len(data["records"]) == 2
    assert data["total_pages"] == 3


def test_get_phone_records_empty_db(test_db):
    """Тест получения записей из пустой БД"""
    response = client.get("/NumberList")
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 0
    assert len(data["records"]) == 0
    assert data["total_pages"] == 1


def test_phone_record_validation_rules(test_db):
    """Тест правил валидации номера телефона"""
    test_cases = [
        ("+79807060972", True),
        ("89807060972", True),
        ("+79123456789", True),
        ("1234567890", False),
        ("+79807", False),
    ]

    for phone_number, should_pass in test_cases:
        data = {
            "data": {
                "number": phone_number,
                "currentDate": str(date.today()),
                "currentTime": datetime.now().strftime('%H:%M:%S'),
                "clickOrder": 1
            }
        }

        response = client.post("/addPhoneNumber", json=data)
        if should_pass:
            assert response.status_code == 200, f"Failed for {phone_number}"
        else:
            assert response.status_code == 422, f"Should fail for {phone_number}"