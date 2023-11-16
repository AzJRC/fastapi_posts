import psycopg
from psycopg.rows import dict_row
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, engine_from_config
from sqlalchemy.orm import sessionmaker
from app.settings import settings
from app.database import Base, get_db
from app.main import app

#create database
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/fastapi_testing"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_from_config)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def get_connection():
    return psycopg.connect(f"user={settings.DB_USER} password={settings.DB_PASSWORD} host={settings.DB_HOSTNAME} port={settings.DB_PORT} dbname={settings.DB_NAME}", 
                           row_factory=dict_row)

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# test root route is working
def test_root():
    response = client.get("/")
    assert response.json() == "Hello world!"
    assert response.status_code == 200


@pytest.mark.parametrize("email, username, password, expectedResponse", 
                         [
                            ("test@gmail.com", "testuser", "password123", {"email": "test@gmail.com", "username": "testuser"}),
                            ("someuser@gmail.com", "someuser", "123456", {"email": "someuser@gmail.com", "username": "someuser"})
                         ]
                        )
def test_user_creation(email, username, password, expectedResponse):
    response = client.post(url="/users", json={"email": email, "username": username, "password": password})
    assert response.json() == expectedResponse
    