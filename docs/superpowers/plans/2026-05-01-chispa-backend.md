# Chispa Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Chispa Python backend — a shared `chispa_core.py` module with all 6 conversation stages, a stateless FastAPI server, and a Kaggle notebook, all powered by Gemma 4 via `google-genai`.

**Architecture:** All stage logic lives in `chispa_core.py` as pure functions. `server.py` is a thin FastAPI wrapper that validates requests, dispatches to core functions via a stage router dict, and returns a stateless JSON response including updated variables and the next stage name. The Kaggle notebook imports or inlines the same core logic for the hackathon submission.

**Tech Stack:** Python 3.10+, `google-genai`, `fastapi`, `uvicorn`, `pydantic`, `python-dotenv`, `pytest`

---

## File Map

| File | Responsibility |
|---|---|
| `chispa_core.py` | All stage functions, prompts verbatim from spec, zero HTTP |
| `server.py` | FastAPI app, Pydantic models, stage router, CORS |
| `chispa_notebook.ipynb` | Kaggle submission, 6 cells, inlines or imports core |
| `requirements.txt` | Pinned dependencies |
| `.env.example` | Template for GOOGLE_API_KEY |
| `.gitignore` | Excludes .env and __pycache__ |
| `tests/__init__.py` | Test package marker |
| `tests/test_core.py` | Unit tests for all chispa_core functions (mocked client) |
| `tests/test_server.py` | Integration tests for FastAPI endpoints |

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create/update: `.gitignore`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create `requirements.txt`**

```
google-genai>=1.0.0
fastapi>=0.111.0
uvicorn>=0.29.0
pydantic>=2.7.0
python-dotenv>=1.0.0
pytest>=8.2.0
httpx>=0.27.0
```

- [ ] **Step 2: Create `.env.example`**

```
GOOGLE_API_KEY=your_key_here
```

- [ ] **Step 3: Create `.gitignore`**

```
.env
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
.ipynb_checkpoints/
```

- [ ] **Step 4: Create `tests/__init__.py`** (empty file)

- [ ] **Step 5: Install dependencies**

Run: `pip install -r requirements.txt`
Expected: all packages install without error

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .env.example .gitignore tests/__init__.py
git commit -m "chore: project setup — deps, env template, test scaffold"
```

---

## Task 2: Core Scaffold — `build_client`, `build_history`, `SYSTEM_PROMPT`

**Files:**
- Create: `chispa_core.py`
- Create: `tests/test_core.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_core.py`:

```python
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
```

- [ ] **Step 2: Run tests — confirm they fail**

Run: `pytest tests/test_core.py -v`
Expected: `ModuleNotFoundError: No module named 'chispa_core'`

- [ ] **Step 3: Create `chispa_core.py` with scaffold**

```python
import json
import os
from google import genai
from google.genai import types

SYSTEM_PROMPT = """You are Chispa — a warm, direct AI companion for working adults who are scared of AI.
Your only job is to guide this person to their first real win with AI in under 20 minutes.

Rules you never break:
1. Never use technical jargon. If a technical word is unavoidable, explain it immediately in plain language.
2. Detect the user's language from their first message. Respond in that language for the entire session. Never switch.
3. Ask exactly ONE question at a time. Never list multiple questions.
4. Never lecture. Never explain before the win. Knowledge comes AFTER the experience.
5. Be warm but efficient. You are a smart friend, not a teacher, not a chatbot, not a course.
6. If the user expresses fear or doubt, acknowledge it in one sentence, then move forward.
7. Never mention that you are an AI model or describe your technical architecture.

Session structure you follow silently:
DISCOVER → PICK → WIN → PILL → MAP
You know which stage you are in. The user does not need to know."""

MODEL = "gemma-4-26b-it"
TEMPERATURE = 0.7
MAX_TOKENS = 1024


def build_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def build_history(turns: list[dict]) -> list[types.Content]:
    return [
        types.Content(
            role=turn["role"],
            parts=[types.Part(text=turn["text"])]
        )
        for turn in turns
    ]


def _call(client: genai.Client, contents, response_json: bool = False) -> str:
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=TEMPERATURE,
        max_output_tokens=MAX_TOKENS,
        **({"response_mime_type": "application/json"} if response_json else {}),
    )
    for attempt in range(2):
        response = client.models.generate_content(
            model=MODEL,
            config=config,
            contents=contents,
        )
        text = response.text or ""
        if text.strip():
            return text
    return ""  # caller handles empty — server returns HTTP 500
```

- [ ] **Step 4: Run tests — confirm they pass**

Run: `pytest tests/test_core.py -v`
Expected: all 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add chispa_core.py tests/test_core.py
git commit -m "feat: core scaffold — SYSTEM_PROMPT, build_client, build_history"
```

---

## Task 3: Stage 1 — `run_discovery`

**Files:**
- Modify: `chispa_core.py`
- Modify: `tests/test_core.py`

- [ ] **Step 1: Write failing tests — append to `tests/test_core.py`**

```python
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
```

- [ ] **Step 2: Run tests — confirm they fail**

Run: `pytest tests/test_core.py::test_run_discovery_returns_parsed_dict -v`
Expected: FAIL with `ImportError` or `AttributeError`

- [ ] **Step 3: Implement `run_discovery` in `chispa_core.py`**

Add after `_call`:

```python
_GENERIC_PHRASES = [
    "save time", "be more productive", "increase efficiency",
    "improve workflow", "work smarter", "do more with less",
]


def _is_generic(use_cases: list) -> bool:
    combined = " ".join(
        f"{uc.get('label', '')} {uc.get('description', '')}".lower()
        for uc in use_cases
    )
    return any(phrase in combined for phrase in _GENERIC_PHRASES)


def run_discovery(client: genai.Client, conversation_history: list) -> dict:
    job_description = conversation_history[-1].parts[0].text

    base_prompt = f"""Input: {job_description}

The user just described their job. Your task:
1. Identify their role in 3 words or less (e.g. "office administrator", "sales assistant")
2. Generate exactly 3 concrete, specific AI use cases for that exact role. Not generic. Not abstract. Real tasks they do every week that AI can help with RIGHT NOW.
3. Frame each use case as a benefit the user gets, not a feature of AI.

Return ONLY valid JSON. No explanation. No preamble.

{{
  "role": "string — their job role in 3 words max",
  "language": "string — ISO 639-1 code of the language they wrote in",
  "use_cases": [
    {{"id": 1, "label": "string — 4 words max, action-oriented", "description": "string — one sentence, plain language"}},
    {{"id": 2, "label": "string", "description": "string"}},
    {{"id": 3, "label": "string", "description": "string"}}
  ]
}}"""

    for attempt in range(2):
        extra = ""
        if attempt == 1:
            extra = "\nReturn ONLY valid JSON, no markdown, no backticks. Each use case must name a specific task they do, not a general benefit."

        contents = list(conversation_history) + [
            types.Content(role="user", parts=[types.Part(text=base_prompt + extra)])
        ]
        raw = _call(client, contents, response_json=True)

        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            if attempt == 0:
                continue
            raise ValueError(f"run_discovery: Gemma 4 returned invalid JSON after 2 attempts: {raw}")

        if _is_generic(data.get("use_cases", [])) and attempt == 0:
            continue

        return data

    raise ValueError("run_discovery: failed to get valid non-generic response")
```

- [ ] **Step 4: Run tests — confirm they pass**

Run: `pytest tests/test_core.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add chispa_core.py tests/test_core.py
git commit -m "feat: stage 1 run_discovery with JSON retry and generic-use-case retry"
```

---

## Task 4: Pill Selector — `select_pill`

**Files:**
- Modify: `chispa_core.py`
- Modify: `tests/test_core.py`

- [ ] **Step 1: Write failing tests — append to `tests/test_core.py`**

```python
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
```

- [ ] **Step 2: Run tests — confirm they fail**

Run: `pytest tests/test_core.py::test_select_pill_writing -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement `select_pill` in `chispa_core.py`**

```python
_PILL_KEYWORDS = {
    1: ["write", "draft", "compose", "email", "letter", "message", "report"],
    2: ["summarize", "summary", "organize", "structure", "notes", "recap"],
    3: ["share", "upload", "data", "spreadsheet", "document", "analyze"],
    4: ["decide", "approve", "review", "act", "action"],
}


def select_pill(selected_use_case: dict) -> int:
    text = f"{selected_use_case.get('label', '')} {selected_use_case.get('description', '')}".lower()
    for pill_id in [1, 2, 3, 4]:
        if any(kw in text for kw in _PILL_KEYWORDS[pill_id]):
            return pill_id
    return 1
```

- [ ] **Step 4: Run tests — confirm they pass**

Run: `pytest tests/test_core.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add chispa_core.py tests/test_core.py
git commit -m "feat: select_pill — rule-based pill selection, no API call"
```

---

## Task 5: Stage 2 — `run_pick_confirm`

**Files:**
- Modify: `chispa_core.py`
- Modify: `tests/test_core.py`

- [ ] **Step 1: Write failing test — append to `tests/test_core.py`**

```python
def test_run_pick_confirm_returns_string():
    from chispa_core import run_pick_confirm, build_history
    client = _mock_client("Perfect — let's actually do this right now, together.")
    history = build_history([{"role": "user", "text": "I work in logistics"}])
    selected_use_case = {"id": 1, "label": "Write emails faster", "description": "Save time on updates"}
    result = run_pick_confirm(client, history, selected_use_case, "office administrator", "en")
    assert isinstance(result, str)
    assert len(result) > 0
```

- [ ] **Step 2: Run test — confirm it fails**

Run: `pytest tests/test_core.py::test_run_pick_confirm_returns_string -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement `run_pick_confirm` in `chispa_core.py`**

```python
def run_pick_confirm(
    client: genai.Client,
    conversation_history: list,
    selected_use_case: dict,
    role: str,
    language: str,
) -> str:
    prompt = f"""Input: {selected_use_case['label']}, {role}, {language}

The user just picked their use case. Write one warm, encouraging sentence that:
- Confirms their choice
- Tells them they're about to do this right now, not learn about it
- Sounds like a smart friend, not a tutor

Respond in {language}. One sentence only. No questions."""

    contents = list(conversation_history) + [
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]
    return _call(client, contents)
```

- [ ] **Step 4: Run tests — confirm they pass**

Run: `pytest tests/test_core.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add chispa_core.py tests/test_core.py
git commit -m "feat: stage 2 run_pick_confirm"
```

---

## Task 6: Stage 3a — `run_win_open`

**Files:**
- Modify: `chispa_core.py`
- Modify: `tests/test_core.py`

- [ ] **Step 1: Write failing test — append to `tests/test_core.py`**

```python
def test_run_win_open_returns_question():
    from chispa_core import run_win_open, build_history
    client = _mock_client("Tell me: who is this email going to, and what needs to be in it?")
    history = build_history([{"role": "user", "text": "I want to write emails faster"}])
    selected_use_case = {"id": 1, "label": "Write emails faster", "description": "Save time on updates"}
    result = run_win_open(client, history, selected_use_case, "office administrator", "en")
    assert isinstance(result, str)
    assert len(result) > 0
```

- [ ] **Step 2: Run test — confirm it fails**

Run: `pytest tests/test_core.py::test_run_win_open_returns_question -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement `run_win_open` in `chispa_core.py`**

```python
def run_win_open(
    client: genai.Client,
    conversation_history: list,
    selected_use_case: dict,
    role: str,
    language: str,
) -> str:
    prompt = f"""Input: {selected_use_case}, {role}, {language}

The user is a {role}. They chose to work on: {selected_use_case['label']} — {selected_use_case['description']}.

Your job now: guide them to complete this task using AI right now.

Step 1: Ask them for the specific details you need to do this task FOR them.
- Ask for ONLY what is strictly necessary. One question maximum.
- Be specific. Not "tell me more" — ask for the exact input you need.

Respond in {language}. One question only."""

    contents = list(conversation_history) + [
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]
    return _call(client, contents)
```

- [ ] **Step 4: Run tests — confirm they pass**

Run: `pytest tests/test_core.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add chispa_core.py tests/test_core.py
git commit -m "feat: stage 3a run_win_open"
```

---

## Task 7: Stage 3b — `run_win_execute` with quality check

**Files:**
- Modify: `chispa_core.py`
- Modify: `tests/test_core.py`

- [ ] **Step 1: Write failing tests — append to `tests/test_core.py`**

```python
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
    # quality check call returns fail, then good output on regenerate
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
```

- [ ] **Step 2: Run tests — confirm they fail**

Run: `pytest tests/test_core.py::test_run_win_execute_returns_output_and_summary -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement `_quality_check` and `run_win_execute` in `chispa_core.py`**

```python
def _quality_check(client: genai.Client, output: str, user_task_details: str, language: str) -> bool:
    prompt = f"""Score this AI output on 3 criteria. Return JSON {{"pass": true}} or {{"pass": false}}.

Criteria:
1. Is the output specific to these user details: "{user_task_details}"? (not generic filler)
2. Is it in language "{language}" with appropriate tone?
3. Would a real person use this as-is without major editing?

Output to score:
{output}"""

    config = types.GenerateContentConfig(
        temperature=0.1,
        max_output_tokens=50,
        response_mime_type="application/json",
    )
    response = client.models.generate_content(
        model=MODEL,
        config=config,
        contents=[types.Content(role="user", parts=[types.Part(text=prompt)])]
    )
    try:
        return json.loads(response.text or "{}").get("pass", True)
    except (json.JSONDecodeError, ValueError):
        return True


def run_win_execute(
    client: genai.Client,
    conversation_history: list,
    selected_use_case: dict,
    user_task_details: str,
    role: str,
    language: str,
) -> dict:
    base_prompt = f"""Input: {selected_use_case}, {user_task_details}, {role}, {language}

The user provided the details needed. Now do the task.
Complete the task fully and well. Do not explain what you are doing. Just do it.
After the output, add ONE short line asking if this looks good.

Respond in {language}."""

    for attempt in range(2):
        extra = ""
        if attempt == 1:
            extra = "\nThe previous output was too generic. Use the exact details provided. Make it specific, professional, and immediately usable."

        contents = list(conversation_history) + [
            types.Content(role="user", parts=[types.Part(text=base_prompt + extra)])
        ]
        output = _call(client, contents)

        if attempt == 0 and not _quality_check(client, output, user_task_details, language):
            continue

        sentences = [s.strip() for s in output.split(".") if s.strip()]
        summary = ". ".join(sentences[:2]) + ("." if sentences else "")
        return {"output": output, "summary": summary}

    sentences = [s.strip() for s in output.split(".") if s.strip()]
    summary = ". ".join(sentences[:2]) + ("." if sentences else "")
    return {"output": output, "summary": summary}
```

- [ ] **Step 4: Run tests — confirm they pass**

Run: `pytest tests/test_core.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add chispa_core.py tests/test_core.py
git commit -m "feat: stage 3b run_win_execute with silent quality check and regeneration"
```

---

## Task 8: Stages 3c, 4, 5 — `run_win_confirm`, `run_pill`, `run_map`

**Files:**
- Modify: `chispa_core.py`
- Modify: `tests/test_core.py`

- [ ] **Step 1: Write failing tests — append to `tests/test_core.py`**

```python
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
```

- [ ] **Step 2: Run tests — confirm they fail**

Run: `pytest tests/test_core.py::test_run_win_confirm_returns_string -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement all three functions in `chispa_core.py`**

```python
def run_win_confirm(client: genai.Client, conversation_history: list, language: str) -> str:
    prompt = f"""Input: {language}

The user just confirmed their AI output looks good. This is their first win.
Write one sentence that celebrates this moment — warm, genuine, not over the top.
Then transition: tell them you want to share something quick about what just happened.

Respond in {language}. Two sentences maximum."""

    contents = list(conversation_history) + [
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]
    return _call(client, contents)


_PILL_NAMES = {
    1: "Prompting",
    2: "AI strengths",
    3: "Context",
    4: "Hallucination",
}

_PILL_DEFINITIONS = {
    1: "What a prompt is + when to be specific vs vague",
    2: "What AI is genuinely good at + when NOT to use it",
    3: "What context means in AI + how much to share at work",
    4: "What hallucination is + when to verify AI output",
}


def run_pill(
    client: genai.Client,
    conversation_history: list,
    pill_id: int,
    selected_use_case: dict,
    role: str,
    language: str,
    task_output_summary: str,
) -> str:
    prompt = f"""Input: {pill_id}, {selected_use_case}, {role}, {language}, {task_output_summary}

Deliver Pill {pill_id} to this user. They are a {role} who just completed: {selected_use_case['label']}.

Pill definition: {_PILL_DEFINITIONS[pill_id]}

Format your pill EXACTLY like this:
1. One sentence naming the concept in plain language (no jargon)
2. One analogy drawn from their specific job/industry (not generic)
3. One question that connects this concept to something they already do at work

Do NOT use bullet points. Write it as natural speech.
Respond in {language}."""

    contents = list(conversation_history) + [
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]
    return _call(client, contents)


def run_map(
    client: genai.Client,
    conversation_history: list,
    role: str,
    selected_use_case: dict,
    pill_id: int,
    language: str,
) -> str:
    pill_concept = _PILL_NAMES.get(pill_id, "Prompting")
    prompt = f"""Input: {role}, {selected_use_case}, {pill_concept}, {language}

The user is a {role}. They just completed their first AI task: {selected_use_case['label']}.
They learned about: {pill_concept}.

Generate their personal AI map: exactly 3 next steps they can take THIS WEEK.

Rules:
- Each step must be specific to their role. Not generic advice.
- Each step must be something they can do in under 30 minutes.
- Each step must build on what they just did — not start over.
- No jargon. No tool names they don't know yet. One free tool recommendation maximum per step.
- Format as numbered list. One sentence per step. Action verb to start.

Respond in {language}."""

    contents = list(conversation_history) + [
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]
    return _call(client, contents)
```

- [ ] **Step 4: Run tests — confirm they pass**

Run: `pytest tests/test_core.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add chispa_core.py tests/test_core.py
git commit -m "feat: stages 3c/4/5 — run_win_confirm, run_pill, run_map"
```

---

## Task 9: FastAPI Server — `server.py`

**Files:**
- Create: `server.py`
- Create: `tests/test_server.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_server.py`:

```python
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
    assert data["model"] == "gemma-4-26b-it"


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
```

- [ ] **Step 2: Run tests — confirm they fail**

Run: `pytest tests/test_server.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'server'`

- [ ] **Step 3: Create `server.py`**

```python
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any

load_dotenv()

from chispa_core import (
    build_client, build_history,
    run_discovery, run_pick_confirm, run_win_open,
    run_win_execute, run_win_confirm, run_pill, run_map,
    select_pill, MODEL,
)

app = FastAPI(title="Chispa API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_client = build_client(os.environ.get("GOOGLE_API_KEY", ""))


class ChatRequest(BaseModel):
    stage: str
    conversation_history: list[dict]
    variables: dict[str, Any] = {}
    user_message: str = ""


class ChatResponse(BaseModel):
    reply: str
    variables: dict[str, Any]
    next_stage: str
    needs_user_input: bool = True


VALID_STAGES = {
    "discovery", "pick_confirm", "win_open",
    "win_execute", "win_confirm", "pill", "map",
}


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if req.stage not in VALID_STAGES:
        raise HTTPException(status_code=422, detail=f"Unknown stage: {req.stage}. Valid: {sorted(VALID_STAGES)}")

    history = build_history(req.conversation_history)
    v = dict(req.variables)

    try:
        if req.stage == "discovery":
            result = run_discovery(_client, history)
            v.update(result)
            return ChatResponse(reply="", variables=v, next_stage="pick_confirm", needs_user_input=False)

        if req.stage == "pick_confirm":
            reply = run_pick_confirm(_client, history, v["selected_use_case"], v["role"], v["language"])
            return ChatResponse(reply=reply, variables=v, next_stage="win_open", needs_user_input=False)

        if req.stage == "win_open":
            reply = run_win_open(_client, history, v["selected_use_case"], v["role"], v["language"])
            return ChatResponse(reply=reply, variables=v, next_stage="win_execute", needs_user_input=True)

        if req.stage == "win_execute":
            result = run_win_execute(
                _client, history, v["selected_use_case"],
                v.get("user_task_details", req.user_message),
                v["role"], v["language"]
            )
            v["task_output"] = result["output"]
            v["task_output_summary"] = result["summary"]
            return ChatResponse(reply=result["output"], variables=v, next_stage="win_confirm", needs_user_input=True)

        if req.stage == "win_confirm":
            reply = run_win_confirm(_client, history, v["language"])
            return ChatResponse(reply=reply, variables=v, next_stage="pill", needs_user_input=False)

        if req.stage == "pill":
            pill_id = select_pill(v["selected_use_case"])
            v["pill_id"] = pill_id
            reply = run_pill(
                _client, history, pill_id, v["selected_use_case"],
                v["role"], v["language"], v.get("task_output_summary", "")
            )
            return ChatResponse(reply=reply, variables=v, next_stage="map", needs_user_input=True)

        if req.stage == "map":
            reply = run_map(_client, history, v["role"], v["selected_use_case"], v.get("pill_id", 1), v["language"])
            return ChatResponse(reply=reply, variables=v, next_stage="done", needs_user_input=False)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

- [ ] **Step 4: Run tests — confirm they pass**

Run: `pytest tests/test_server.py -v`
Expected: all tests PASS

- [ ] **Step 5: Smoke test the running server**

Run in one terminal: `uvicorn server:app --reload --port 8000`

Run in another:
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"ok","model":"gemma-4-26b-it"}`

- [ ] **Step 6: Commit**

```bash
git add server.py tests/test_server.py
git commit -m "feat: fastapi server with stage router, pydantic models, CORS"
```

---

## Task 10: Kaggle Notebook — `chispa_notebook.ipynb`

**Files:**
- Create: `chispa_notebook.ipynb`

- [ ] **Step 1: Create the notebook**

Create `chispa_notebook.ipynb` with the following cell structure. The notebook inlines `chispa_core` content so it is fully self-contained for Kaggle upload.

**Cell 1 — Setup and imports:**
```python
# Cell 1: Setup
!pip install -q google-genai

import json, os, sys
from google import genai
from google.genai import types
```

**Cell 2 — Inline core or import:**
```python
# Cell 2: Load Chispa core
# If chispa_core.py is uploaded alongside this notebook, use:
# from chispa_core import *
# Otherwise, paste the full chispa_core.py content here:

# --- paste full chispa_core.py content here ---
```

**Cell 3 — API key and client:**
```python
# Cell 3: API key
# On Kaggle: add GOOGLE_API_KEY as a Kaggle Secret
from kaggle_secrets import UserSecretsClient
secrets = UserSecretsClient()
os.environ["GOOGLE_API_KEY"] = secrets.get_secret("GOOGLE_API_KEY")

client = build_client(os.environ["GOOGLE_API_KEY"])
print("Client ready.")
```

**Cell 4 — Discovery:**
```python
# Cell 4: Discovery
print("Hi! I'm Chispa. I'm here to help you do something real with AI — today, in the next 20 minutes.\n")
user_input = input("First question: what do you do for work?\n> ")

conversation_history = [{"role": "user", "text": user_input}]
result = run_discovery(client, build_history(conversation_history))
conversation_history.append({"role": "model", "text": json.dumps(result)})

print(f"\nRole detected: {result['role']}")
print(f"Language: {result['language']}\n")
print("Here's what we can do right now:\n")
for uc in result["use_cases"]:
    print(f"  {uc['id']}. {uc['label']} — {uc['description']}")

variables = {
    "role": result["role"],
    "language": result["language"],
    "use_cases": result["use_cases"],
}
```

**Cell 5 — Pick and full flow:**
```python
# Cell 5: Pick + Win + Pill + Map
choice = int(input("\nPick 1, 2, or 3: ")) - 1
variables["selected_use_case"] = variables["use_cases"][choice]

# Pick confirm
confirm = run_pick_confirm(client, build_history(conversation_history),
                           variables["selected_use_case"], variables["role"], variables["language"])
conversation_history.append({"role": "model", "text": confirm})
print(f"\nChispa: {confirm}\n")

# Win open
question = run_win_open(client, build_history(conversation_history),
                        variables["selected_use_case"], variables["role"], variables["language"])
conversation_history.append({"role": "model", "text": question})
print(f"Chispa: {question}")
task_details = input("> ")
conversation_history.append({"role": "user", "text": task_details})
variables["user_task_details"] = task_details

# Win execute
win_result = run_win_execute(client, build_history(conversation_history),
                             variables["selected_use_case"], task_details,
                             variables["role"], variables["language"])
variables["task_output"] = win_result["output"]
variables["task_output_summary"] = win_result["summary"]
conversation_history.append({"role": "model", "text": win_result["output"]})

print(f"\n--- Chispa's output ---\n{win_result['output']}\n-----------------------")
feedback = input("\nDoes this look good? (yes / tell me what to fix): ")
conversation_history.append({"role": "user", "text": feedback})

if feedback.strip().lower() not in ("yes", "y", "sí", "si", "oui", "ja"):
    conversation_history.append({"role": "user", "text": f"Fix this: {feedback}"})
    win_result = run_win_execute(client, build_history(conversation_history),
                                 variables["selected_use_case"], f"{task_details}. Fix: {feedback}",
                                 variables["role"], variables["language"])
    variables["task_output"] = win_result["output"]
    variables["task_output_summary"] = win_result["summary"]
    conversation_history.append({"role": "model", "text": win_result["output"]})
    print(f"\n--- Revised output ---\n{win_result['output']}\n----------------------")

# Win confirm
win_msg = run_win_confirm(client, build_history(conversation_history), variables["language"])
conversation_history.append({"role": "model", "text": win_msg})
print(f"\nChispa: {win_msg}\n")

# Pill
pill_id = select_pill(variables["selected_use_case"])
variables["pill_id"] = pill_id
pill_text = run_pill(client, build_history(conversation_history), pill_id,
                     variables["selected_use_case"], variables["role"],
                     variables["language"], variables["task_output_summary"])
conversation_history.append({"role": "model", "text": pill_text})
print(f"💡 What just happened:\n{pill_text}\n")
```

**Cell 6 — Map:**
```python
# Cell 6: Personal map (hackathon visible output)
map_text = run_map(client, build_history(conversation_history),
                   variables["role"], variables["selected_use_case"],
                   variables["pill_id"], variables["language"])
print("═" * 50)
print("YOUR NEXT 3 STEPS")
print("This week. Your job. No jargon.")
print("═" * 50)
print(map_text)
print("═" * 50)
print("\nOne spark. That's how it starts.\n— Chispa")
```

- [ ] **Step 2: Verify notebook is valid JSON**

Run: `python -c "import json; json.load(open('chispa_notebook.ipynb')); print('valid')"`
Expected: `valid`

- [ ] **Step 3: Commit**

```bash
git add chispa_notebook.ipynb
git commit -m "feat: kaggle notebook — 6-cell chispa flow, self-contained submission"
```

---

## Task 11: Full End-to-End Smoke Test

- [ ] **Step 1: Run full test suite**

Run: `pytest tests/ -v`
Expected: all tests PASS, 0 failures

- [ ] **Step 2: Start the server and call discovery with a real API key**

Requires `GOOGLE_API_KEY` set in `.env`.

```bash
uvicorn server:app --reload --port 8000
```

```bash
curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "stage": "discovery",
    "conversation_history": [{"role": "user", "text": "I work as an office assistant in logistics"}],
    "variables": {},
    "user_message": "I work as an office assistant in logistics"
  }' | python -m json.tool
```

Expected: JSON response with `variables.role`, `variables.use_cases` (3 items), `next_stage: "pick_confirm"`

- [ ] **Step 3: Final commit**

```bash
git add .
git commit -m "chore: backend complete — core, server, notebook all wired up"
```

---

## Running the Server

```bash
# Install
pip install -r requirements.txt

# Set API key
cp .env.example .env
# edit .env and add GOOGLE_API_KEY=your_key

# Run
uvicorn server:app --reload --port 8000

# Test
pytest tests/ -v
```

Server runs at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.
