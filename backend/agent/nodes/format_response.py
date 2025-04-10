from state import AgentState

def format_response(state: AgentState):

    matches = state.get("robot_matches", [])

    if not matches:
        state["messages"] = state.get("messages", []) + [
            {"role": "agent", "content": "I couldn't find any matching robots for this task. You can try rephrasing or adjusting the requirements."}
        ]
        return state

    robot_summaries = []
    for robot in matches:
        summary = f"{robot['name']} (SDK: {robot['sdk']}, Max Payload: {robot.get('max_payload')}kg)"
        robot_summaries.append(summary)

    message = {
        "role": "agent",
        "content": "Here are some robot options for your task:\n" + "\n".join(robot_summaries)
    }

    state["messages"] = state.get("messages", []) + [message]
    return state