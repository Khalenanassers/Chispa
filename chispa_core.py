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
