from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app=app)

def test_root():
    response = client.get("/")
    print(response)
    assert response == "Hello world!"
    assert response.status_code == 200