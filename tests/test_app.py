import sys
import os

# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from unittest.mock import AsyncMock
from app.main import app   # <-- THIS must import FastAPI instance
import app.main

# ---------------- MOCK DATABASE ----------------

fake_row = {
    "id": 1,
    "title": "CI Test Task",
    "description": "Testing CI pipeline",
    "completed": False,
}

mock_db = AsyncMock()
mock_db.fetchrow.return_value = fake_row
mock_db.fetch.return_value = [fake_row]
mock_db.execute.return_value = "OK"

# Replace real DB with mock
app.main.db = mock_db

client = TestClient(app)

# ---------------- TESTS ----------------

def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200


def test_create_task_success():
    response = client.post(
        "/tasks",
        json={"title": "CI Test Task", "description": "Testing CI pipeline"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "CI Test Task"