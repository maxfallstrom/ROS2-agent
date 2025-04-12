from helpers.summarize_chat_history import summarize_context_for_embedding
from helpers.vector_search import search_robots
from state import AgentState

async def query_urdfs(state: AgentState) -> dict:
    
    messages = state.get("messages", [])
    
    summary = await summarize_context_for_embedding(messages)

    state["summary_query"] = summary

    try:
        matches = search_robots(summary, threshold=0.3)
    except Exception as e:
        state["error"] = str(e)
        state["matches"] = []
        state.setdefault("messages", []).append({
            "role": "assistant",
            "content": "Sorry, I had trouble searching for robots. Please try again or rephrase your request."
        })
        return state

    state["matches"] = matches

    if matches:
        robot_names = [match["name"] for match in matches]
        message = (
            f"Based on your needs, here are some robots you might like:\n\n" +
            "\n".join(f"- {name}" for name in robot_names) +
            "\n\nWould you like to learn more about one of them? Also, feel free to explore the robots in the view!"
        )
    else:
        message = (
            "I couldn't find any robots that match your request exactly."
            "You can try rephrasing your request or giving me a bit more detail."
        )

    state.setdefault("messages", []).append({
        "role": "assistant",
        "content": message
    })

    return state
