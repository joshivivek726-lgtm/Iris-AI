import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.routes import LLMService


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        LLMService, "generate_response", staticmethod(lambda prompt, history=None: "fake reply")
    )
    return TestClient(app)


def test_root_is_running(client):
    assert client.get("/").json()["status"] == "running"


def test_chat_creates_conversation(client):
    r = client.post("/api/chat", json={"message": "Hello", "user_id": "pytest_user"})
    assert r.status_code == 200
    body = r.json()
    assert body["response"] == "fake reply"
    assert body["conversation_id"].startswith("conv_")


def test_chat_unknown_conversation_returns_404(client):
    r = client.post(
        "/api/chat",
        json={"message": "Hi", "user_id": "pytest_user", "conversation_id": "conv_doesnotexist"},
    )
    assert r.status_code == 404


def test_chat_empty_message_rejected(client):
    r = client.post("/api/chat", json={"message": "   ", "user_id": "pytest_user"})
    assert r.status_code in (400, 422)