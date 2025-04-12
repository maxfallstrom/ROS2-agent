from state import AgentState
from helpers.classify_prompt import classify_prompt, PromptClassification

async def parse_prompt(state: AgentState):
    
    user_input = state["input"]
    state.setdefault("messages", []).append({
        "role": "user",
        "content": user_input
    })

    classification: PromptClassification = await classify_prompt(state)

    state["status"] = classification.status

    if classification.question:
        state.setdefault("messages", []).append({
            "role": "assistant",
            "content": classification.question
        })


    return state
