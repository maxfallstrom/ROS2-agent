from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict
from app.state_manager import load_state, save_state, clear_state
from  uuid import UUID
from agent.graph_agent import robot_agent
from app.dto import convert_to_dto

router = APIRouter()

class PromptRequest(BaseModel):
    user_id: UUID
    session_id: UUID
    prompt: str
    metadata: Optional[Dict] = None

@router.post("/prompt")
async def handle_prompt(request: PromptRequest):

    state = load_state(request.session_id)

    messages = state.get("messages", [])
    messages.append({"role": "user", "content": request.prompt})
    state["messages"] = messages
    state["user_id"] = request.user_id

    result = await robot_agent.astream(state)

    async for output in result:
        state.update(output)

    save_state(request.session_id, state)

    return convert_to_dto(state)

@router.post("/followup")
async def handle_followup(request: PromptRequest):
    state = load_state(str(request.session_id))

    messages = state.get("messages", [])
    messages.append({"role": "user", "content": request.prompt})
    state["messages"] = messages

    result = await robot_agent.astream(state)
    async for output in result:
        state.update(output)

    save_state(str(request.session_id), state)

    return convert_to_dto(state)