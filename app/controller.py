from fastapi import APIRouter
from app.state_manager import load_state, save_state, clear_state
from agent.graph_agent import robot_agent
from app.responses.prompt_response import convert_to_response
from app.responses.action_response import convert_to_action_response
from requests.prompt_request import PromptRequest
from requests.action_request import ActionRequest

router = APIRouter()

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

    return convert_to_response(state)

@router.post("/followup")
async def handle_followup(request: PromptRequest):
    state = load_state(request.session_id)

    messages = state.get("messages", [])
    messages.append({"role": "user", "content": request.prompt})
    state["messages"] = messages

    result = await robot_agent.astream(state)
    async for output in result:
        state.update(output)

    save_state(request.session_id, state)

    return convert_to_response(state)

@router.post("/action")
async def handle_action(request: ActionRequest):
    state = load_state(request.session_id)
    state["selected_robot"] = request.selected_robot
    state["action_prompt"] = request.action_prompt

    result = await robot_agent.astream(state)
    async for output in result:
        state.update(output)

    save_state(request.session_id, state)

    return convert_to_action_response(state)
