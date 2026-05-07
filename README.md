![License](https://img.shields.io/badge/license-Proprietary-red)
![Hackathon](https://img.shields.io/badge/Gemma%204%20Good%20Hackathon-Kaggle%20%C3%97%20Google%20DeepMind-blue)
![Track](https://img.shields.io/badge/track-Digital%20Equity-green)

# Chispa ✦

**An AI companion that takes a working adult from fear to their first real win with AI — in under 20 minutes.**

Built for the [Gemma 4 Good Hackathon](https://www.kaggle.com/competitions/gemma-4-good) · Kaggle × Google DeepMind · Digital Equity track.

---

## The Problem

Millions of working adults — especially those 40–55 years old — are watching AI reshape their industries. They feel the threat. They have no time, no money for bootcamps, and no safe place to start.

Most upskilling tools are built *for* tech-savvy people *about* tech topics. The people who most need AI literacy are the last to get it.

**This is not an education problem. It is an economic survival problem.**

---

## The Solution

Chispa (Spanish: *spark*) meets users at the moment before they give up — and turns it into their first win.

It is not a course. Not a chatbot. Not a tool directory. It is an **onboarding experience for real life.**

```
"What do you do for work?"
        ↓
Gemma 4 maps their job to 3 real, concrete AI uses
        ↓
User picks the one that fits right now
        ↓
Chispa walks them through it — live, together
        ↓
They produce something real
        ↓
✦ EUFORIA — the spark
        ↓
The Pill: one concept, one analogy, one question
        ↓
The Map: 3 personalized next steps for this week
```

The knowledge pill lands *after* the win, not before. The win creates the context; the pill creates the understanding.

---

## Who It's For

**Rosa, 45.** Office clerk. Two kids. Her job is her family's income. She's heard AI is going to change everything. She has 20 minutes and a lot of fear.

- Non-technical. No coding background.
- Multilingual — may not be an English native speaker.
- Time-poor. Won't finish a 10-hour course.
- Has real daily tasks: emails, reports, scheduling, documents.

Chispa reaches Rosa through people she already trusts: HR departments sharing it during "AI readiness" briefings, union newsletters, multilingual WhatsApp groups. No app store. No account. Just a shared link.

---

## Technical Stack

| Layer | Technology |
|---|---|
| Model | Gemma 4 26B MoE via Google AI Studio API |
| Backend | Python — FastAPI (`server.py`) |
| Frontend | React JSX, single-file (`index.html`) |
| Hosting | Kaggle Notebook (primary), Hugging Face Spaces |

**Why Gemma 4:** Multilingual by default (35+ languages), open-weight so it can run locally — meaning sensitive workplace data never has to leave the user's device. That's not a technical detail. It's why a 45-year-old office clerk can use this at work without asking IT.

---

## Running Locally

```bash
# 1. Clone and set up
git clone https://github.com/Khalenanassers/Chispa.git
cd Chispa
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

# 2. Add your API key
echo GOOGLE_API_KEY=your_key_here > .env

# 3. Start the server
uvicorn server:app --reload

# 4. Open http://localhost:8000
```

---

## Running Tests

```bash
pytest          # all tests (no API key required — all mocked)
pytest tests/test_server.py -v
```

---

## Six Screens, One Emotional Arc

| Screen | Emotional job |
|---|---|
| 1 · Landing | Reduce fear, zero friction |
| 2 · Discovery | Make the user feel heard |
| 3 · Pick | Make choosing feel exciting |
| 4 · The Win | Build momentum → euforia |
| 5 · The Pill | Create the "aha" |
| 6 · The Map | Leave with direction, not overwhelm |

---

## License

Copyright (c) 2026 Khalena Nasser. All Rights Reserved.
See [LICENSE](LICENSE) for full terms.

This project is shared for hackathon evaluation only. Forking, redistribution, and derivative works are prohibited.
