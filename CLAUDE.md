# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Session Setup

At the start of every session, invoke these skills in order:

| Skill | When |
|---|---|
| `caveman` | Always — sets compressed communication mode |
| `superpowers:brainstorming` | Before any feature, screen, or UI work |
| `impeccable` | When designing or building any screen or UI component |
| `superpowers:writing-plans` | Before any multi-step implementation |
| `superpowers:systematic-debugging` | On any bug or unexpected behavior |
| `simplify` | After completing a major implementation step |

---

## Dev Commands

```bash
# Setup (Windows — activate venv first)
.venv\Scripts\activate
pip install -r requirements.txt

# .env (create at project root — only this key is needed)
# GOOGLE_API_KEY=your_key_here

# Run backend (requires GOOGLE_API_KEY in .env)
uvicorn server:app --reload

# Run all tests (no API key needed — all mocked)
pytest

# Run a single test
pytest tests/test_core.py::test_run_discovery_returns_parsed_dict -v

# Run server tests only
pytest tests/test_server.py -v
```

---

## Code Architecture

Three files carry all application logic:

**`chispa_core.py`** — pure stage functions, no HTTP. Each stage is one exported `run_*` function (`run_discovery`, `run_pick_confirm`, `run_win_open`, `run_win_execute`, `run_win_confirm`, `run_pill`, `run_map`). Also exports `select_pill` (rule-based, no AI) and `build_history`/`build_client` helpers. All AI calls go through the internal `_call()` helper which retries once on empty response. `run_win_execute` makes an extra low-temperature self-critique call via `_quality_check()` and silently regenerates on failure.

**`server.py`** — stateless FastAPI. Endpoints: `GET /` (serves `index.html`), `GET /health` (model name check), `POST /api/chat` (main). The `stage` string routes to the matching `run_*` function. **The frontend owns all state** — it sends `variables` (a dict) on every request and receives it back updated. `selected_use_case` is set by the frontend (user taps a card), not by any AI call. `build_history()` converts `list[dict]` wire format into `list[types.Content]` on every request.

**`index.html`** — deployed frontend (~1170 lines, self-contained). All 6 screens, design tokens, animations, and API calls in one file. Served by `GET /`, talks to `POST /api/chat`, manages all conversation state client-side. **`Chispa.jsx`** (~976 lines, also at project root) is the React source equivalent — edit this for development. There is no automated build step: changes made in `Chispa.jsx` must be manually ported into `index.html` (the JSX is inlined as a `<script type="text/babel">` block). The `frontend/` and `backend/` directories are empty scaffolding and unused.

**`chispa_notebook.ipynb`** — Kaggle notebook for hosted deployment. Handles ngrok tunnel, secret injection, and server startup. Edit this when changing the Kaggle hosting setup.

Stage routing in `server.py` (linear, no branching):

| Stage | `next_stage` | `needs_user_input` |
|---|---|---|
| `discovery` | `pick_confirm` | false — auto-advances |
| `pick_confirm` | `win_open` | false — auto-advances |
| `win_open` | `win_execute` | true — waits for task details |
| `win_execute` | `win_confirm` | true — waits for "looks good" |
| `win_confirm` | `pill` | false — auto-advances |
| `pill` | `map` | true — waits for user response |
| `map` | `done` | false — session ends |

---

## What This Is

**Chispa** is an AI companion that guides non-technical working adults through their first real win with AI in under 20 minutes. Built for the Gemma 4 Good Hackathon (Kaggle × Google DeepMind, Digital Equity track). **Deadline: May 18, 2026.**

Primary persona: Rosa, 45, office clerk. Multilingual, time-poor, emotionally blocked. Chispa reaches her via HR briefings, WhatsApp groups, union newsletters — no app store, no account required.

The product is built around a single emotional peak: *euforia* — the moment Rosa realizes she just used AI to do something real. Every design and architecture decision exists to reach that moment as fast as possible.

---

## Spec Documents

| File | Role | Read when... |
|---|---|---|
| `chispa_prd.md` | WHY and WHAT — product goals, persona, architecture | Getting context or writing technical write-up |
| `chispa_prompt_spec.md` | THE BRAIN — all prompt text, stage logic, API calls | Building the backend / Python |
| `chispa_ux_brief.md` | THE BODY — 6 screens, design tokens, motion rules | Building the frontend / React |
| `chispa_studio_handover.md` | Build order — step-by-step sequence | Orienting on where to start |
| `docs/superpowers/specs/` | Design decisions and technical specs per feature | Understanding why something was built a certain way |
| `docs/superpowers/plans/` | Step-by-step implementation plans from past sessions | Resuming or reviewing prior work |

---

## Technical Stack

| Layer | Technology |
|---|---|
| Model | Gemma 4 26B MoE via Google AI Studio API (`gemma-4-26b-a4b-it`) |
| Backend | Python — FastAPI (`server.py`) |
| Frontend | React JSX single-file component, or plain HTML/JS |
| Hosting | Kaggle Notebook or Hugging Face Spaces (free tier) |
| Local dev | Ollama (`ollama run gemma4:e4b`) |

---

## Conversation Flow — 6 Stages

The session follows a fixed linear path. The user never sees stage labels.

```
STAGE 0 — SYSTEM PROMPT   (loaded once at session start, never changes)
STAGE 1 — DISCOVERY       (user describes job → JSON: role + 3 use cases)
STAGE 2 — PICK            (pure UI — user taps one of 3 cards, no AI call)
STAGE 3 — THE WIN         (multi-turn: collect details → execute task → confirm)
STAGE 4 — THE PILL        (one concept + analogy + question, rule-based pill selection)
STAGE 5 — THE MAP         (3 personalized next steps, auto-fires after pill)
```

### Variable Chain (must persist across all API calls)

```
user_input → role → language → use_cases[3]
           → selected_use_case → user_task_details
           → task_output → task_output_summary  (first 2 sentences of task_output)
           → pill_id → map[3]
```

`pill_id` (1–4) is the only pill variable stored in `variables`. Pill concept name is resolved internally in `run_map` via `_PILL_NAMES` dict — never stored in `variables`.

Pass the **full conversation history** on every API call.

---

## API Reference

Stage 1 uses `response_mime_type: application/json` for reliable structured output. All other stages use plain text.

### Stage 1 JSON schema

```json
{
  "role": "string (3 words max)",
  "language": "ISO 639-1 code",
  "use_cases": [
    { "id": 1, "label": "string (4 words max)", "description": "string (one sentence)" },
    { "id": 2, "label": "string", "description": "string" },
    { "id": 3, "label": "string", "description": "string" }
  ]
}
```

### Pill selection logic (rule-based, no AI call)

`select_pill()` scans `selected_use_case.label + description` for keywords. Priority order: **2 → 3 → 4 → 1**. Pill 1 is the fallback when no keywords match.

| Pill | Keywords matched |
|---|---|
| Pill 2 — AI strengths | summarize, summary, organize, structure, notes, recap |
| Pill 3 — Context | share, upload, data, spreadsheet, document, analyze |
| Pill 4 — Hallucination | decide, approve, review, act, action |
| Pill 1 — Prompting | write, draft, compose, email, letter, message, report (or fallback) |

---

## Frontend — 6 Screens

Each screen has one emotional job. Build for the emotion, not the feature.

| Screen | Emotional job |
|---|---|
| 1 Landing | Reduce fear, zero friction |
| 2 Discovery | Make user feel heard |
| 3 Pick (3 cards) | Make choosing feel exciting |
| 4 Win (guided task) | Build momentum → euforia |
| 5 Pill | Create the "aha" |
| 6 Map | Leave with direction, no overwhelm |

**Do not skip the euforia moment** (Screen 4, after "✓ This is great"): full-screen Warm Sand flash → "✦ There it is." → win message → auto-transition after 2.5s. This is the product.

---

## Design System Tokens

```
Background:     #264653   (all screens)
Surface:        #1e363f   (cards, input areas)
Primary:        #e76f51   (CTAs, Chispa name — Burnt Orange)
Accent:         #f4a261   (hover, secondary actions — Coral)
Highlight:      #e9c46a   (euforia + pill ONLY — Warm Sand)
Text Primary:   #f1faee   (body text — warm cream)
Text Secondary: #a8b8bc   (hints, labels)
Border:         #3d5a66   (card borders)
User messages:  #c25240   (coral bubble, right-aligned)
```

**Hard rules:**
- `#e9c46a` Warm Sand is reserved for euforia and pill only — never use elsewhere
- Never use `#00F0C0` (Khalena's teal brand color) anywhere in Chispa
- Background must feel warm, not cold

**Typography:** Syne 800 for headlines, DejaVu Sans for body, IBM Plex Mono 400 for output cards only.

**Layout:** Mobile-first, max-width 480px, 24px horizontal padding, 12px card border-radius. All transitions 300ms ease-in-out.

---

## Key Constraints

- **No account. No sign-up. No email.** Zero friction — Rosa arrives via a shared link.
- **Multilingual by default.** Gemma 4 auto-detects language from first message and never switches back. No language selector UI.
- **One flow, six screens.** No nav, no history sidebar, no settings, no profile. Single-session only in v1.
- **"Save my map"** must work without an account — copy to clipboard minimum.
- Input bar on Screen 2 and 4 must rise with the mobile keyboard (handle viewport resize).

---

## Failure Handling

| Situation | Response |
|---|---|
| Stage 1 JSON malformed | Retry once with "Return ONLY valid JSON, no markdown, no backticks." |
| Use cases too generic | Add: "Each use case must name a specific task they do, not a general benefit." |
| Output fails quality check | Regenerate silently once. Never show a failed output. Never tell the user. |
| User says output is bad | "Tell me what to fix — I'll redo it." Regenerate with their feedback as correction. |
| Gemma 4 returns empty | Retry once, then display: "Give me a second — I'm thinking." |
| User expresses fear/anxiety | One acknowledgment sentence, then continue. Never stall on the emotion. |
