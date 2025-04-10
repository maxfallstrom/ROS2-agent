from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from state import AgentState

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

SYSTEM_INSTRUCTION = """
You're an assistant helping to identify missing information for selecting a robot.
Based on the following list of missing fields, ask clear, concise follow-up questions to the user.

Respond with a message that helps the user provide this missing info. Be brief, specific, and user-friendly.
"""

def ask_missing_info(state: AgentState):

    missing = state.get("missing_fields", [])
    if not missing:
        return state

    user_msg = f"Missing fields: {', '.join(missing)}"

    response = llm.invoke([
        SystemMessage(content=SYSTEM_INSTRUCTION),
        HumanMessage(content=user_msg)
    ])

    followup = {
        "role": "agent",
        "content": response.content
    }

    messages = state.get("messages", [])
    messages.append(followup)
    state["messages"] = messages

    return state