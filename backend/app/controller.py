from fastapi import APIRouter
from app.state_manager import load_state, save_state
from agent.graph_agent import robot_agent
from app.responses.prompt_response import convert_stream_chunk
from app.requests.prompt_request import PromptRequest
from fastapi.responses import StreamingResponse
import json
from agent.state import AgentState
from typing import cast

router = APIRouter()

@router.post("/prompt")
async def handle_prompt(request: PromptRequest):

    state: AgentState = load_state(request.session_id) or cast(AgentState, {})

    state.setdefault("messages", [])

    state["messages"].append({
        "role": "user",
        "content": request.prompt
    })

    async def event_stream():
        try:
            async for output in robot_agent.astream(state):
                state.update(output)
                chunk = convert_stream_chunk(state)
                yield f"data: {json.dumps(chunk)}\n\n"

        except Exception as e:
            state["error"] = str(e)
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        finally:
            save_state(request.session_id, state)
    

    return StreamingResponse(event_stream(), media_type="text/event-stream")
