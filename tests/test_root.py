import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.settings import settings
from app.database import Base, get_db
from app.main import app
from app.utils import hash_password

#create database
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/fastapi_testing"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# test root route is working
def test_root():
    response = client.get(url="/")
    assert response.json() == "Hello world!"
    assert response.status_code == 200

TEST_USER_1 = {"email": "test@gmail.com", "username": "testuser"}
TEST_USER_2 = {"email": "someuser@gmail.com", "username": "someuser"}
TEST_PASSWORD = "password123"

@pytest.mark.parametrize("email, username, password, expectedResponse", 
    [
    (TEST_USER_1["email"], TEST_USER_1["username"], TEST_PASSWORD, TEST_USER_1),
    (TEST_USER_2["email"], TEST_USER_2["username"], TEST_PASSWORD, TEST_USER_2)
    ]
)
def test_user_creation(email, username, password, expectedResponse):
    print("test user creation ->")
    response = client.post(url="/users", json={"email": email, "username": username, "password": password})
    assert response.json() == expectedResponse
    assert response.status_code == 201

@pytest.mark.parametrize("username, password", [
    (TEST_USER_1["email"], TEST_PASSWORD),
    (TEST_USER_2["username"], TEST_PASSWORD)
])
def test_user_login_and_deletion(username, password):
    print("test login ->")
    response = client.post(url="/login", data={"username": username, "password": password})
    assert response.status_code == 200

    print("test deletion ->")
    response2 = client.delete(url="/users", headers={"Authorization": f"{response.json()['token_type']} {response.json()['access_token']}"})
    assert response2.status_code == 204

    