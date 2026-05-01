import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any

load_dotenv()

from chispa_core import (
    build_client, build_history,
    run_discovery, run_pick_confirm, run_win_open,
    run_win_execute, run_win_confirm, run_pill, run_map,
    select_pill, MODEL,
)

app = FastAPI(title="Chispa API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_client = build_client(os.environ.get("GOOGLE_API_KEY", ""))


class ChatRequest(BaseModel):
    stage: str
    conversation_history: list[dict]
    variables: dict[str, Any] = {}
    user_message: str = ""


class ChatResponse(BaseModel):
    reply: str
    variables: dict[str, Any]
    next_stage: str
    needs_user_input: bool = True


VALID_STAGES = {
    "discovery", "pick_confirm", "win_open",
    "win_execute", "win_confirm", "pill", "map",
}


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if req.stage not in VALID_STAGES:
        raise HTTPException(status_code=422, detail=f"Unknown stage: {req.stage}. Valid: {sorted(VALID_STAGES)}")

    history = build_history(req.conversation_history)
    v = dict(req.variables)

    try:
        if req.stage == "discovery":
            result = run_discovery(_client, history)
            v.update(result)
            return ChatResponse(reply="", variables=v, next_stage="pick_confirm", needs_user_input=False)

        if req.stage == "pick_confirm":
            reply = run_pick_confirm(_client, history, v["selected_use_case"], v["role"], v["language"])
            return ChatResponse(reply=reply, variables=v, next_stage="win_open", needs_user_input=False)

        if req.stage == "win_open":
            reply = run_win_open(_client, history, v["selected_use_case"], v["role"], v["language"])
            return ChatResponse(reply=reply, variables=v, next_stage="win_execute", needs_user_input=True)

        if req.stage == "win_execute":
            result = run_win_execute(
                _client, history, v["selected_use_case"],
                v.get("user_task_details", req.user_message),
                v["role"], v["language"]
            )
            v["task_output"] = result["output"]
            v["task_output_summary"] = result["summary"]
            return ChatResponse(reply=result["output"], variables=v, next_stage="win_confirm", needs_user_input=True)

        if req.stage == "win_confirm":
            reply = run_win_confirm(_client, history, v["language"])
            return ChatResponse(reply=reply, variables=v, next_stage="pill", needs_user_input=False)

        if req.stage == "pill":
            pill_id = select_pill(v["selected_use_case"])
            v["pill_id"] = pill_id
            reply = run_pill(
                _client, history, pill_id, v["selected_use_case"],
                v["role"], v["language"], v.get("task_output_summary", "")
            )
            return ChatResponse(reply=reply, variables=v, next_stage="map", needs_user_input=True)

        if req.stage == "map":
            reply = run_map(_client, history, v["role"], v["selected_use_case"], v.get("pill_id", 1), v["language"])
            return ChatResponse(reply=reply, variables=v, next_stage="done", needs_user_input=False)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
