# Chispa

**A multilingual AI companion that takes working adults from fear to their first win with AI — in one session, around their specific job.**

---

## The Problem

Millions of working adults are watching AI reshape their industries with no time, money, or safe space to start. Most upskilling tools are built for tech-savvy people about tech topics. The people who need AI literacy most are the last to get it.

---

## What Chispa Does

Chispa guides users through one real task using AI — drafting an email, summarizing a document, structuring a recap. After the win, it explains what just happened (one concept, one analogy, one question). Then it gives them three next steps specific to their job.

The session takes 20 minutes. No account. No install. Works in any phone browser.

---

## The Core Loop

- User describes their job
- Gemma 4 maps it to 3 concrete AI use cases
- User picks one
- Chispa guides them through doing it live
- User produces a real output
- Chispa delivers one knowledge concept (the Pill)
- Chispa delivers 3 personalized next steps (the Map)

---

## Built With

| Layer | Technology |
|---|---|
| Model | Gemma 4 26B MoE via Google AI Studio API (`gemma-4-26b-a4b-it`) |
| Backend | Python + FastAPI |
| Frontend | React (single-file, CDN) |
| Notebook | Kaggle (free GPU tier, T4) |
| Tunnel | ngrok (for public URL from Kaggle) |

---

## Why Gemma 4

- Native multilingual support (35+ languages) — auto-detects user language
- Multimodal — users can upload documents
- On-device capable (E4B architecture) — user data can stay local in v2
- Apache 2.0 license — no commercial restrictions

---

## How to Run (Local)

**Terminal 1 — Backend:**
```bash
cd Chispa
python server.py
```
Runs at `http://localhost:8000`

**Terminal 2 — Frontend:**
```bash
npm run dev
```
Opens at `http://localhost:5173`

---

## How to Run (Kaggle)

1. Open `chispa_notebook_v2.ipynb` in Kaggle
2. Add your Google AI Studio API key in Cell 1
3. Run All (cells in order)
4. Cell 9 prints the public ngrok URL
5. Open on phone to demo

---

## Hackathon

Gemma 4 Good Hackathon · Kaggle × Google DeepMind  
Track: Digital Equity  
Deadline: May 18, 2026

---

## License

All rights reserved — Khalena Nasser.  
Permitted for hackathon evaluation only.  
Contact: [khalenanasser.com](https://khalenanasser.com)
