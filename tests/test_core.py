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


SAMPLE_EMAIL_OUTPUT = (
    "Dear Maria,\n\nHere is the weekly logistics update for the Hamburg depot.\n"
    "All shipments are on schedule. Three deliveries pending for Friday.\n\nBest regards,\nRosa"
)


def test_run_win_execute_returns_output_and_summary():
    from chispa_core import run_win_execute, build_history
    client = _mock_client(SAMPLE_EMAIL_OUTPUT)
    history = build_history([{"role": "user", "text": "weekly update email for Maria, formal"}])
    selected_use_case = {"id": 1, "label": "Write emails faster", "description": "Save time"}
    result = run_win_execute(
        client, history, selected_use_case,
        "weekly logistics update for manager Maria, formal tone",
        "office administrator", "en"
    )
    assert "output" in result
    assert "summary" in result
    assert len(result["output"]) > 0
    assert len(result["summary"]) > 0


def test_run_win_execute_summary_is_shorter_than_output():
    from chispa_core import run_win_execute, build_history
    client = _mock_client(SAMPLE_EMAIL_OUTPUT)
    history = build_history([{"role": "user", "text": "update email"}])
    selected_use_case = {"id": 1, "label": "Write emails faster", "description": "Save time"}
    result = run_win_execute(
        client, history, selected_use_case,
        "update email for Maria", "office administrator", "en"
    )
    assert len(result["summary"]) <= len(result["output"])


def test_run_win_execute_regenerates_on_quality_fail():
    from chispa_core import run_win_execute, build_history

    short_generic = "Here is your email."
    good_output = SAMPLE_EMAIL_OUTPUT

    client = MagicMock()
    resp1 = MagicMock(); resp1.text = short_generic
    resp2 = MagicMock(); resp2.text = good_output
    quality_fail = MagicMock(); quality_fail.text = '{"pass": false}'
    client.models.generate_content.side_effect = [resp1, quality_fail, resp2]

    history = build_history([{"role": "user", "text": "weekly update"}])
    selected_use_case = {"id": 1, "label": "Write emails faster", "description": "Save time"}
    result = run_win_execute(
        client, history, selected_use_case,
        "weekly logistics update for Maria", "office administrator", "en"
    )
    assert client.models.generate_content.call_count == 3
    assert result["output"] == good_output


def test_run_win_confirm_returns_string():
    from chispa_core import run_win_confirm, build_history
    client = _mock_client("You just did that in 3 minutes. Let me show you what you actually did.")
    history = build_history([{"role": "user", "text": "This looks great!"}])
    result = run_win_confirm(client, history, "en")
    assert isinstance(result, str)
    assert len(result) > 0


def test_run_pill_returns_string():
    from chispa_core import run_pill, build_history
    client = _mock_client("What you just did is called prompting. Think of it like briefing a colleague. What else do you brief people on?")
    history = build_history([{"role": "user", "text": "This is great!"}])
    selected_use_case = {"id": 1, "label": "Write emails faster", "description": "Save time"}
    result = run_pill(client, history, 1, selected_use_case, "office administrator", "en", "Weekly logistics update email for Maria.")
    assert isinstance(result, str)
    assert len(result) > 0


def test_run_map_returns_string():
    from chispa_core import run_map, build_history
    client = _mock_client("1. Use AI to draft your next meeting recap.\n2. Upload a document and ask AI for the 3 key points.\n3. Ask AI to help you find the right tone for a difficult message.")
    history = build_history([{"role": "user", "text": "Got it!"}])
    selected_use_case = {"id": 1, "label": "Write emails faster", "description": "Save time"}
    result = run_map(client, history, "office administrator", selected_use_case, 1, "en")
    assert isinstance(result, str)
    assert len(result) > 0
