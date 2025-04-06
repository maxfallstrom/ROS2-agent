from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import json
from state import AgentState

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SYSTEM_INSTRUCTIONS = """
Extract the following fields from the user's prompt. Do not add anything for the fields you cannot extract info for.

Respond ONLY in valid JSON with keys:
- task_description: What the robot is supposed to do
- terrain_type: "indoor", "outdoor", or "unknown"
- payload_kg: Estimated numeric value (float), or null if unknown
"""


def parse_prompt(state: AgentState):
    # Get prompt
    user_prompt = state["messages"][-1]["content"]

    # Invoke LLM
    response = llm.invoke([SystemMessage(content=SYSTEM_INSTRUCTIONS), HumanMessage(content=user_prompt)])

    try:
        parsed = json.loads(response.content)
    except Exception as e:
        parsed = {
            "task_description": user_prompt,
            "terrain_type": None,
            "payload_kg": None,
            "error": f"Parse failed: {e}"
        }

    state["task_description"] = parsed.get("task_description")
    state["terrain_type"] = parsed.get("terrain_type")
    state["payload_kg"] = parsed.get("payload_kg")

    return state
