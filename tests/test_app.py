from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_or_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200


def test_create_task_validation():
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_create_task_success():
    response = client.post(
        "/tasks",
        json={
            "title": "CI Test Task",
            "description": "Testing CI pipeline"
        },
    )
    assert response.status_code in (200, 201)