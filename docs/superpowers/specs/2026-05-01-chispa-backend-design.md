# Chispa Backend Design
**Date:** 2026-05-01
**Scope:** Python backend — `chispa_core.py`, `server.py`, `chispa_notebook.ipynb`
**Status:** Approved

---

## Decisions

| Decision | Choice | Reason |
|---|---|---|
| Deployment targets | Both Kaggle notebook + FastAPI server | Hackathon submission + UI demo |
| Session state | Stateless — frontend owns history | Simpler, maps cleanly to notebook structure |
| SDK | `google-genai` (new) | Matches prompt spec exactly |
| Architecture | Shared core module + thin wrappers | One source of truth, no drift |

---

## File Structure

```
D:\Claude\Chispa\
├── chispa_core.py          ← stage logic, pure functions, no HTTP
├── server.py               ← FastAPI app, imports chispa_core
├── chispa_notebook.ipynb   ← Kaggle submission, imports/inlines chispa_core
├── requirements.txt
└── .env                    ← GOOGLE_API_KEY (gitignored)
```

---

## Data Contracts

### API Request (`POST /api/chat`)
```json
{
  "stage": "discovery | win_open | win_execute | win_confirm | pill | map",
  "conversation_history": [{"role": "user|model", "text": "..."}],
  "variables": {
    "role": "string",
    "language": "ISO 639-1 code",
    "selected_use_case": {"id": 1, "label": "...", "description": "..."},
    "user_task_details": "string",
    "task_output_summary": "string",
    "pill_id": 1
  },
  "user_message": "string"
}
```

### API Response
```json
{
  "reply": "string",
  "variables": {"role": "...", "language": "...", "use_cases": [...], "...": "..."},
  "next_stage": "string"
}
```

Only the keys relevant to the current stage need to be present in `variables`. Each stage adds its output keys to the chain and returns the full updated dict.

---

## `chispa_core.py` — Stage Functions

### Initialization
```python
SYSTEM_PROMPT: str           # Stage 0 — loaded once, never changes
build_client(api_key) → genai.Client
build_history(turns: list[dict]) → list[Content]
# converts [{"role": "user", "text": "..."}] → google-genai Content objects
```

### Stage 1 — Discovery

The hardcoded opening message ("Hi! I'm Chispa...") is displayed by the **frontend** without an API call. The first API call happens only after the user submits their job description.

```python
run_discovery(client, conversation_history) → dict
# {"role": str, "language": str, "use_cases": [{"id", "label", "description"}]}
# uses response_mime_type="application/json"
# retry once on malformed JSON with stricter instruction
# retry once if use cases are too generic
```

### Stage 2 — Pick
No function. Pure UI — frontend sends `selected_use_case` back as a variable.

### Stage 3 — Win (three sequential calls)
```python
run_win_open(client, history, selected_use_case, role, language) → str
# Chispa's one question asking for the minimum details needed

run_win_execute(client, history, selected_use_case, user_task_details, role, language) → dict
# {"output": str, "summary": str}
# output = full task text shown to user
# summary = first 2 sentences of output, passed to run_pill as task_output_summary
# Runs internal quality check (3 criteria) before returning
# Silently regenerates once if check fails — never exposes failure to user

run_win_confirm(client, history, language) → str
# Celebration + transition sentence (two sentences max)
```

### Stage 4 — Pill
```python
select_pill(selected_use_case) → int    # rule-based, no API call
# writing → 1, summarizing → 2, sharing data → 3, any output to act on → 4
# default: 1

run_pill(client, history, pill_id, selected_use_case, role, language, task_output_summary) → str
# One concept + one job-specific analogy + one transfer question
# No bullet points — natural speech
```

### Stage 5 — Map
```python
run_map(client, history, role, selected_use_case, pill_id, language) → str
# Numbered list, 3 steps, one sentence each, action verb first
# Specific to role, doable in under 30 min, builds on the win
```

### Shared config applied to all calls
- Model: `gemma-4-26b-it`
- Temperature: `0.7`
- Max output tokens: `1024`
- `response_mime_type: "application/json"` — Stage 1 only

---

## `server.py` — FastAPI

### Endpoints
```
GET  /health         → {"status": "ok", "model": "gemma-4-26b-it"}
POST /api/chat       → request/response as per Data Contracts above
```

### Route logic
- `stage_router` dict maps stage name → core function (no if/elif chain)
- Pydantic models validate request and response shapes
- `python-dotenv` loads `.env` at startup
- CORS open (`*`) for local dev
- HTTP 422 on unknown stage name
- HTTP 500 with `{"error": str}` if Gemma 4 fails after retries

---

## `chispa_notebook.ipynb` — Kaggle

6 cells:

| Cell | Purpose |
|---|---|
| 1 | `pip install`, imports, load `chispa_core` (inline if Kaggle can't resolve module) |
| 2 | API key from Kaggle Secrets, `build_client()` |
| 3 | Run discovery — `input()` → `run_discovery()` → print use cases |
| 4 | Pick use case — `input()` for choice, set `selected_use_case` |
| 5 | Run win → pill → map — full loop, each turn appends to history |
| 6 | Print final map as notebook visible output for submission |

---

## Error Handling

| Situation | Handling |
|---|---|
| Stage 1 JSON malformed | Retry once with stricter instruction |
| Stage 1 use cases too generic | Retry once with specificity instruction |
| Stage 3 output fails quality check | Regenerate once silently |
| User says output is bad | Re-run `win_execute` with user feedback as correction |
| Gemma 4 empty response | Retry once; server returns HTTP 500 after second failure |
| Unknown stage in POST /api/chat | HTTP 422 |

---

## Requirements

```
google-genai
fastapi
uvicorn
pydantic
python-dotenv
```

---

## Out of Scope (v1)

- Authentication / API key protection on the server
- Persistent session storage
- Rate limiting
- Streaming responses
- Multimodal input (document upload)
- Offline / on-device Gemma 4 E4B fallback
