import json
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
