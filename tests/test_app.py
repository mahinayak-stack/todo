import sys
import os

# ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from core.main import app

client = TestClient(app)


def test_health():
    res = client.get("/")
    assert res.status_code == 200


def test_create_todo():
    res = client.post(
        "/todos",
        json={"title": "CI Task", "description": "Testing"},
    )
    assert res.status_code == 200
    assert res.json()["title"] == "CI Task"


def test_get_todos():
    res = client.get("/todos")
    assert res.status_code == 200
    assert len(res.json()) > 0


def test_update_todo():
    res = client.put(
        "/todos/1",
        json={"title": "Updated", "description": "Updated desc"},
    )
    assert res.status_code == 200


def test_delete_todo():
    res = client.delete("/todos/1")
    assert res.status_code == 200