# Chispa — Product Requirements Document
**Hackathon:** Gemma 4 Good Hackathon · Kaggle × Google DeepMind
**Track:** Digital Equity
**Deadline:** May 18, 2026 · 23:59 UTC
**Builder:** Khalena Nasser · Solo
**Status:** Active Priority

---

## 01 · The Problem

Millions of working adults — especially those 40–55 years old — are watching AI reshape their industries. They feel the threat. They have no time, no money for bootcamps, and no safe space to start. Most upskilling tools are built *for* tech-savvy people *about* tech topics.

The result: people who most need AI literacy are the last to get it.

**This is not an education problem. It is an economic survival problem.**

---

## 02 · The Solution — What Chispa Is

> **Chispa** is a multilingual AI companion that takes a working adult from fear to their **first step toward AI literacy** in one session — through a real task, a conceptual spark, and a strategic map built around their specific job.

**Chispa** (Spanish: *spark*) targets the moment before someone gives up — and turns it into their first win.

It is not a course. Not a chatbot. Not a tool directory.
It is an **onboarding experience for real life.**

### The Design Goal
The product is not built around information delivery. It is built around an **emotional peak**: *euforia* — the adrenaline rush of discovering you are capable of something you were afraid of. Every design decision has one job: get the user to their first win as fast as possible.

### The Educational Theory
This is grounded in **self-efficacy** (Bandura) and **mastery experience**. The single most powerful predictor of learning is whether someone believes they *can*. Chispa manufactures that belief through a real experience, not through encouragement.

### Why Not Just Use ChatGPT?
Rosa handles sensitive company emails, logistics documents, and internal reports. Sending that data to a third-party cloud API is a real workplace risk — many employers prohibit it explicitly. Chispa is built on Gemma 4, an open-weight model that can run locally on-device. Her data never leaves her phone. That is not a technical detail — it is the reason a 45-year-old office assistant can actually use this at work without asking her IT department for permission.

### How Rosa Finds Chispa
Chispa reaches Rosa through the people she already trusts: HR departments sharing it as a free tool during "AI readiness" briefings, union newsletters, and multilingual WhatsApp groups where working adults share useful resources. No app store. No ad campaign. Word of mouth in the language she speaks.

---

## 03 · Who It's For

**Primary persona:** Rosa, 45 years old. Office clerk or administrative assistant. Two kids. Her job is her family's income. She's heard AI is going to change everything. She doesn't know where to start. She has 20 minutes and a lot of fear.

**Key attributes:**
- Non-technical. No coding background.
- Multilingual — may not be an English native speaker.
- Time-poor. Won't finish a 10-hour course.
- Emotionally blocked — fear and imposter syndrome are the real barriers.
- Has real daily work tasks (emails, reports, scheduling, documents).

**What she needs:** Not to *learn about AI*. For AI to *learn about her* — her job, her language — and show her exactly what to do this week.

---

## 04 · The Core Loop

```
"What do you do for work?"
        ↓
Gemma 4 maps their job to 3 real, concrete AI uses
        ↓
Picks the easiest one for right now
        ↓
Walks them through doing it. Live. Together.
        ↓
They produce something real.
        ↓
EUFORIA ← this is the product
        ↓
The Pill: "Here's what you just did, and why it works."
        ↓
The Map: "Here are your 3 next steps."
```

**The key principle:** The knowledge pill lands *after* the win, not before. Learning attaches to experience. The win creates the context; the pill creates the understanding.

---

## 05 · The Three Layers

### Layer 1 — The Spark (First Win)
**Time:** 0–20 minutes
**Goal:** The user produces something real using AI.

- Chispa asks: *"What do you do for work? What takes up most of your time?"*
- Gemma 4 identifies their role and maps it to 3 concrete AI uses.
- Chispa picks the lowest-friction one for the session.
- Guides them step by step through doing it live.
- Output: a real artifact — a drafted email, a summarized document, a structured list.

**For the office clerk demo:**
User complains about spending an hour writing update emails every Monday.
→ Chispa shows them how to draft it with AI in 3 minutes.
→ They see the output. That's the spark.

### Layer 2 — The Pill (Conceptual + Strategic Literacy)
**Time:** Right after the win
**Goal:** They understand *what* they just did and *when* to use it.

Not a lecture. A revelation. Format: **One sentence naming the concept + one analogy from their real world + one question that creates transfer.**

**Knowledge framework:** Conceptual + Strategic (not mechanical).

| Pill | Concept | Strategic Layer |
|---|---|---|
| 1 | What a prompt is | When to be specific vs. vague |
| 2 | What AI is good at | When NOT to use it |
| 3 | What context means | How much to share with AI at work |
| 4 | What hallucination is | When to verify the output |

**Example Pill — Office clerk who just drafted an email:**
> *"What you just did is called prompting. Think of it like briefing a very fast colleague — the clearer your instructions, the better their work. What else do you brief people on every day?"*

That last question is the transfer mechanism. They stop being a student and start being someone who already knows how to do this.

### Layer 3 — The Map (Personal Path)
**Time:** End of session
**Goal:** Three next steps specific to their job. No jargon. Actionable this week.

Gemma 4 generates the map based on:
- Their job role
- The task they just completed
- The pill they absorbed

Output format: Three sentences. Three next steps. One URL or tool per step maximum.

---

## 06 · Technical Architecture

### Model
**Primary:** Gemma 4 26B MoE via Google AI Studio API
**Planned v2:** Gemma 4 E4B on-device (offline fallback — not in v1 scope)

**Why Gemma 4:**
- Multilingual — native support for 35+ languages, pre-trained on 140+
- Multimodal — user can show their actual work (a document, a form photo)
- On-device capable in future — E4B architecture supports local deployment for data privacy
- Apache 2.0 — no commercial restrictions, no data sent to third parties when run locally
- On Kaggle notebooks — pre-loaded, no setup

### Stack
| Layer | Technology |
|---|---|
| Model | Gemma 4 via Google AI Studio API |
| Backend | Python (FastAPI or Flask) |
| Frontend | React or simple HTML/JS (single file) |
| Notebook | Kaggle Notebook (GPU: T4/P100 free tier) |
| Local dev | Ollama (`ollama run gemma4:e4b`) |
| Hosting | Kaggle or Hugging Face Spaces (free) |

### Key Gemma 4 Features Used
- **Native multilingual** — language detection + response in user's language
- **Function calling** — structured job-to-use-case mapping
- **Long context (256K)** — full conversation history maintained
- **System prompt support** — Chispa's persona and rules loaded at session start
- **Multimodal input** — user can upload a document for the live task

### System Prompt (core)
```
You are Chispa — a warm, direct AI companion for working adults who are new to AI.
Your job is to guide the user to their first real win with AI in under 20 minutes.
Rules:
- Never use jargon unless you explain it immediately after.
- Match the user's language automatically. If they write in Spanish, respond in Spanish.
- Ask one question at a time. Never overwhelm.
- When you identify their job, map it to exactly 3 concrete AI uses. Pick the simplest one.
- After the win, deliver one Pill: one concept, one analogy, one question.
- End every session with exactly 3 next steps specific to their job.
- Your tone is warm, direct, and encouraging — like a smart friend, not a teacher.
```

---

## 07 · Multilingual Strategy

**Priority languages:** Spanish, English, German, Portuguese, French
**Approach:** Gemma 4 auto-detects language from first user input and responds in kind. No language selection UI needed. This is the differentiator — it feels native, not translated.

**Why this matters for the hackathon:** The target user (Rosa) may not be an English speaker. Multilingual-first is not a feature — it's the whole thesis of accessibility.

---

## 08 · Demo Script (Submission Video)

**Character:** Rosa, 45, office clerk. Hamburg. Works in logistics admin.
**Pain:** Spends every Monday morning writing status update emails to 3 different managers. Takes 1 hour. She hates it.

**Demo flow (5 minutes):**
1. Rosa opens Chispa on her phone. Types: *"I'm an office assistant, I work in logistics."*
2. Chispa responds warmly, identifies her role, offers 3 AI uses.
3. Rosa picks "write emails faster."
4. Chispa asks: *"Tell me what the email is about. Who's it for? What needs to be in it?"*
5. Rosa describes her Monday update email.
6. Chispa drafts it. Rosa reads it. It's good.
7. **The euforia moment.** Rosa says: "That took 3 minutes."
8. Chispa delivers the Pill: the prompting concept, the colleague analogy.
9. Chispa delivers Rosa's personal map: 3 next steps.
10. End card: Chispa logo + "One spark. That's how it starts."

---

## 09 · Hackathon Submission Requirements

| Requirement | Status | Owner |
|---|---|---|
| Working prototype | Build | Khalena |
| Public GitHub repo | Setup Week 1 | Khalena |
| Technical write-up | Write Week 3 | Khalena |
| Demo video (real-world use) | AI-generated Week 3 | Khalena |
| Kaggle notebook submission | Final Week 3 | Khalena |

**Judging criteria this submission targets:**
- ✅ Social impact — economic survival for non-technical workers
- ✅ Technical execution — real Gemma 4 integration, multilingual, multimodal-ready
- ✅ Real-world use case — specific user, specific pain, measurable win
- ✅ Data privacy — Gemma 4 open-weight architecture means user data stays local, no third-party API exposure
- ✅ Constrained environment — works on any phone browser, no app install required

---

## 10 · 18-Day Sprint Plan

### Week 1 — Core (Apr 30 – May 6)
- [ ] Day 1–2: Kaggle account setup + Google AI Studio API key. Gemma 4 responding to basic prompt.
- [ ] Day 3–4: Build Discovery conversation flow. "What do you do?" → 3 AI uses mapped.
- [ ] Day 5–7: Build First Win flow for office clerk. End-to-end working. Euforia moment live.

### Week 2 — Depth (May 7 – May 13)
- [ ] Day 8–9: Build Pill system. 4 pills triggered contextually post-win.
- [ ] Day 10–11: Build Personal Map. Gemma 4 generates 3 next steps per user.
- [ ] Day 12–13: Add Spanish. Test multilingual switching.
- [ ] Day 14: UI pass. Clean enough to feel real.

### Week 3 — Submit (May 14 – May 18)
- [ ] Day 15–16: Produce AI-generated demo video. Rosa character, full flow, euforia moment. Use AI video tool (e.g. Runway, Kling, or HeyGen).
- [ ] Day 17: Technical write-up for Kaggle submission.
- [ ] Day 18: Submit. Buffer for bugs.

---

## 11 · What Chispa Is NOT

- Not a course platform
- Not a chatbot with an FAQ
- Not a tool comparison site
- Not a generic "AI for everyone" app
- Not built for tech-savvy users
- Not dependent on a specific language or country
- Not exposing user data to third-party clouds (architecture allows local deployment in v2)

---

## 12 · The One Sentence

> Chispa is the spark that turns fear into the first win — and the first win into the first step on a path that belongs to them.

---

*Document created: April 30, 2026*
*Author: Khalena Nasser*
*Contact: khalenanasser.com · linkedin.com/in/khalenanassers*
