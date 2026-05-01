import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with patch("server.build_client") as mock_build:
        mock_build.return_value = MagicMock()
        from server import app
        return TestClient(app)


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["model"] == "gemma-4-26b-a4b-it"


def test_chat_unknown_stage_returns_422(client):
    response = client.post("/api/chat", json={
        "stage": "not_a_real_stage",
        "conversation_history": [],
        "variables": {},
        "user_message": "hello"
    })
    assert response.status_code == 422


def test_chat_discovery_returns_reply_and_variables(client):
    discovery_result = {
        "role": "office administrator",
        "language": "en",
        "use_cases": [
            {"id": 1, "label": "Write emails faster", "description": "Save time"},
            {"id": 2, "label": "Summarize documents", "description": "Read faster"},
            {"id": 3, "label": "Draft reports", "description": "Finish reports quickly"},
        ]
    }
    with patch("server.run_discovery", return_value=discovery_result):
        response = client.post("/api/chat", json={
            "stage": "discovery",
            "conversation_history": [{"role": "user", "text": "I work in logistics"}],
            "variables": {},
            "user_message": "I work as an office administrator"
        })
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert "variables" in data
    assert data["variables"]["role"] == "office administrator"
    assert data["next_stage"] == "pick_confirm"


def test_chat_win_confirm_sets_next_stage_pill(client):
    with patch("server.run_win_confirm", return_value="You did it! Let me share something."):
        response = client.post("/api/chat", json={
            "stage": "win_confirm",
            "conversation_history": [{"role": "user", "text": "This is great!"}],
            "variables": {"language": "en"},
            "user_message": "This is great!"
        })
    assert response.status_code == 200
    assert response.json()["next_stage"] == "pill"
