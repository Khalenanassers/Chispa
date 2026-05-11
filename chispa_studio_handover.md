# Chispa — Google AI Studio Handover
**What this is:** The exact order and context for using these documents to build Chispa.

---

## THE THREE FILES AND WHAT THEY DO

| File | What it is | Give to AI when... |
|---|---|---|
| `chispa_prd.md` | The WHY and WHAT | You need context or are writing the technical write-up |
| `chispa_prompt_spec.md` | The BRAIN | You are building the backend / API calls |
| `chispa_ux_brief.md` | The BODY | You are building the frontend / UI |

---

## STEP-BY-STEP ORDER FOR GOOGLE AI STUDIO

### STEP 1 — Test the system prompt (Day 1)
**Where:** Google AI Studio → New prompt → System instructions
**Paste:** The STAGE 0 system prompt from `chispa_prompt_spec.md`
**Then type:** "I work as an office assistant in logistics"
**Goal:** Confirm Gemma 4 responds warmly and asks the right first question.
**Model to use:** gemma-4-26b-it

---

### STEP 2 — Test Stage 1 discovery prompt (Day 1–2)
**Where:** Google AI Studio → same session
**Paste:** Stage 1 prompt from `chispa_prompt_spec.md` with a test job description
**Goal:** Get clean JSON back with role + 3 use cases
**Watch for:** Generic use cases — if you get them, add the failure handling instruction

---

### STEP 3 — Build the full prompt chain in a notebook (Day 2–3)
**Where:** Kaggle Notebook
**Provide the AI:** `chispa_prompt_spec.md` + this instruction:

> "Build a Python script that runs the full Chispa conversation flow using the Google AI Studio API. Use the prompt spec exactly as written. Stages 0–5. Store all variables. Pass full conversation history on each call."

---

### STEP 4 — Build the UI (Day 5–7)
**Provide the AI:** `chispa_ux_brief.md` + this instruction:

> "Build a single-file React component (JSX) that implements the Chispa UI exactly as described in this brief. All 6 screens. Use the design system tokens defined. Connect to the Python backend via fetch calls."

---

### STEP 5 — Connect and test end-to-end (Day 7)
**Provide the AI both files + this instruction:**

> "Connect the Chispa React frontend to the Python backend. The frontend should call /api/chat with the full conversation history on each user message. The backend runs the prompt chain from the spec. Test the full flow: landing → discovery → pick → win → pill → map."

---

## THE ONE PROMPT TO START RIGHT NOW

Copy this into Google AI Studio immediately to test if Gemma 4 behaves as Chispa:

```
SYSTEM:
You are Chispa — a warm, direct AI companion for working adults who are scared of AI.
Your only job is to guide this person to their first real win with AI in under 20 minutes.
Rules: Never use jargon. Match the user's language automatically. Ask ONE question at a time. Never lecture before the win. Be like a smart friend, not a teacher.

USER:
I work as an office assistant. I handle emails, scheduling, and documents for a logistics company.
```

**Expected behavior:** Chispa identifies the role, offers exactly 3 concrete use cases as JSON, warm tone, no jargon.

If it works — you're ready to build. If it doesn't — adjust temperature (try 0.7) and add "Return ONLY valid JSON, no markdown fences."

---

*Handover created: April 30, 2026*
