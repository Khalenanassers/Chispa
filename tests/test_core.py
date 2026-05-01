import pytest
from unittest.mock import MagicMock, patch
from google.genai import types


def test_system_prompt_is_non_empty():
    from chispa_core import SYSTEM_PROMPT
    assert isinstance(SYSTEM_PROMPT, str)
    assert len(SYSTEM_PROMPT) > 100
    assert "Chispa" in SYSTEM_PROMPT


def test_build_history_user_message():
    from chispa_core import build_history
    turns = [{"role": "user", "text": "I work in logistics"}]
    result = build_history(turns)
    assert len(result) == 1
    assert result[0].role == "user"
    assert result[0].parts[0].text == "I work in logistics"


def test_build_history_model_message():
    from chispa_core import build_history
    turns = [{"role": "model", "text": "Hi! I'm Chispa."}]
    result = build_history(turns)
    assert result[0].role == "model"


def test_build_history_multiple_turns():
    from chispa_core import build_history
    turns = [
        {"role": "user", "text": "Hello"},
        {"role": "model", "text": "Hi there"},
        {"role": "user", "text": "I work as a nurse"},
    ]
    result = build_history(turns)
    assert len(result) == 3
    assert result[2].parts[0].text == "I work as a nurse"


def test_build_client_returns_client():
    from chispa_core import build_client
    with patch("chispa_core.genai.Client") as mock_client_cls:
        mock_client_cls.return_value = MagicMock()
        client = build_client("fake-key")
        mock_client_cls.assert_called_once_with(api_key="fake-key")
        assert client is not None
