from agent.state import AgentState
from agent.helpers.classify_prompt import classify_prompt, PromptClassification

async def parse_prompt(state: AgentState):
    
    user_input = state["messages"][-1]["content"]
    
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
