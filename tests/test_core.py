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


import json

VALID_DISCOVERY_JSON = json.dumps({
    "role": "office administrator",
    "language": "en",
    "use_cases": [
        {"id": 1, "label": "Write emails faster", "description": "Save time on weekly updates"},
        {"id": 2, "label": "Summarize documents", "description": "Read reports in seconds"},
        {"id": 3, "label": "Draft meeting notes", "description": "Never miss action items"},
    ]
})

GENERIC_DISCOVERY_JSON = json.dumps({
    "role": "office administrator",
    "language": "en",
    "use_cases": [
        {"id": 1, "label": "Save time", "description": "Be more productive"},
        {"id": 2, "label": "Increase efficiency", "description": "Improve workflow"},
        {"id": 3, "label": "Work smarter", "description": "Do more with less"},
    ]
})


def _mock_client(response_text: str) -> MagicMock:
    client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = response_text
    client.models.generate_content.return_value = mock_resp
    return client


def test_run_discovery_returns_parsed_dict():
    from chispa_core import run_discovery, build_history
    client = _mock_client(VALID_DISCOVERY_JSON)
    history = build_history([{"role": "user", "text": "I work as an office administrator in logistics"}])
    result = run_discovery(client, history)
    assert result["role"] == "office administrator"
    assert result["language"] == "en"
    assert len(result["use_cases"]) == 3
    assert result["use_cases"][0]["id"] == 1


def test_run_discovery_retries_on_malformed_json():
    from chispa_core import run_discovery, build_history
    client = MagicMock()
    bad_resp = MagicMock()
    bad_resp.text = "not valid json"
    good_resp = MagicMock()
    good_resp.text = VALID_DISCOVERY_JSON
    client.models.generate_content.side_effect = [bad_resp, good_resp]
    history = build_history([{"role": "user", "text": "I work in HR"}])
    result = run_discovery(client, history)
    assert client.models.generate_content.call_count == 2
    assert result["role"] == "office administrator"


def test_run_discovery_retries_on_generic_use_cases():
    from chispa_core import run_discovery, build_history
    client = MagicMock()
    generic_resp = MagicMock()
    generic_resp.text = GENERIC_DISCOVERY_JSON
    good_resp = MagicMock()
    good_resp.text = VALID_DISCOVERY_JSON
    client.models.generate_content.side_effect = [generic_resp, good_resp]
    history = build_history([{"role": "user", "text": "I work in logistics"}])
    result = run_discovery(client, history)
    assert client.models.generate_content.call_count == 2
    assert result["use_cases"][0]["label"] == "Write emails faster"


def test_select_pill_writing():
    from chispa_core import select_pill
    uc = {"id": 1, "label": "Write emails faster", "description": "Draft weekly updates quickly"}
    assert select_pill(uc) == 1


def test_select_pill_summarizing():
    from chispa_core import select_pill
    uc = {"id": 2, "label": "Summarize reports", "description": "Organize key points from documents"}
    assert select_pill(uc) == 2


def test_select_pill_sharing_data():
    from chispa_core import select_pill
    uc = {"id": 3, "label": "Analyze spreadsheet", "description": "Share your data and get insights"}
    assert select_pill(uc) == 3


def test_select_pill_defaults_to_1():
    from chispa_core import select_pill
    uc = {"id": 3, "label": "Something unusual", "description": "An edge case not matching any keyword"}
    assert select_pill(uc) == 1


def test_run_pick_confirm_returns_string():
    from chispa_core import run_pick_confirm, build_history
    client = _mock_client("Perfect — let's actually do this right now, together.")
    history = build_history([{"role": "user", "text": "I work in logistics"}])
    selected_use_case = {"id": 1, "label": "Write emails faster", "description": "Save time on updates"}
    result = run_pick_confirm(client, history, selected_use_case, "office administrator", "en")
    assert isinstance(result, str)
    assert len(result) > 0


def test_run_win_open_returns_question():
    from chispa_core import run_win_open, build_history
    client = _mock_client("Tell me: who is this email going to, and what needs to be in it?")
    history = build_history([{"role": "user", "text": "I want to write emails faster"}])
    selected_use_case = {"id": 1, "label": "Write emails faster", "description": "Save time on updates"}
    result = run_win_open(client, history, selected_use_case, "office administrator", "en")
    assert isinstance(result, str)
    assert len(result) > 0
