import json
import time
from google import genai
from google.genai import types
from google.genai.errors import ServerError

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

MODEL = "gemma-4-26b-a4b-it"
FALLBACK_MODEL = "gemini-2.5-flash"
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
    )
    if response_json:
        # Do NOT use response_mime_type — triggers 500 on Gemma
        # JSON instruction lives in the caller's prompt text
        pass

    last_error = None
    for attempt in range(3):
        try:
            print(f"[Chispa] API call attempt {attempt + 1}/3...", flush=True)
            response = client.models.generate_content(
                model=MODEL,
                config=config,
                contents=contents,
            )
            return response.text.strip()
        except ServerError as e:
            last_error = e
            if attempt < 2:
                wait = (attempt + 1) * 5  # 5s, then 10s
                time.sleep(wait)
    raise last_error


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

        if isinstance(data, list):
            data = {"role": "unknown", "language": "en", "use_cases": data}

        if _is_generic(data.get("use_cases", [])) and attempt == 0:
            continue

        return data

    raise ValueError("run_discovery: failed to get valid non-generic response")


_PILL_KEYWORDS = {
    1: ["write", "draft", "compose", "email", "letter", "message", "report"],
    2: ["summarize", "summary", "organize", "structure", "notes", "recap"],
    3: ["share", "upload", "data", "spreadsheet", "document", "analyze"],
    4: ["decide", "approve", "review", "act", "action"],
}


def select_pill(selected_use_case: dict) -> int:
    text = f"{selected_use_case.get('label', '')} {selected_use_case.get('description', '')}".lower()
    for pill_id in [2, 3, 4, 1]:
        if any(kw in text for kw in _PILL_KEYWORDS[pill_id]):
            return pill_id
    return 1


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

    output = ""
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
