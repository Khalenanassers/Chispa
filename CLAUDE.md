# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Session Setup

At the start of every session, invoke these skills in order:

| Skill | When |
|---|---|
| `caveman` | Always — sets compressed communication mode |
| `superpowers:brainstorming` | Before any feature, screen, or UI work |
| `ui-ux-pro-max` | When designing or building any screen |
| `frontend-design` | When building React/HTML components |
| `superpowers:writing-plans` | Before any multi-step implementation |
| `superpowers:systematic-debugging` | On any bug or unexpected behavior |
| `simplify` | After completing a major implementation step |

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

---

## Technical Stack

| Layer | Technology |
|---|---|
| Model | Gemma 4 26B MoE via Google AI Studio API (`gemma-4-26b-it`) |
| Backend | Python — FastAPI or Flask |
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
           → task_output → task_output_summary
           → pill_id → pill_concept_name → map[3]
```

Pass the **full conversation history** on every API call.

---

## API Call Structure

```python
response = client.models.generate_content(
    model="gemma-4-26b-it",
    config={
        "system_instruction": SYSTEM_PROMPT,
        "temperature": 0.7,
        "max_output_tokens": 1024,
        "response_mime_type": "application/json"  # Stage 1 ONLY
    },
    contents=conversation_history
)
```

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

| Use case involves | Pill |
|---|---|
| Writing, drafting, composing | Pill 1 — Prompting |
| Summarizing, organizing, structuring | Pill 2 — AI strengths |
| Sharing info with AI (emails, docs, data) | Pill 3 — Context |
| Any output the user will act on | Pill 4 — Hallucination |

Default: always fire Pill 1 on first session.

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
