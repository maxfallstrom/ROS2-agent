from state import AgentState

def check_info(state: AgentState):

    missing_fields = []

    # Only have two requirements for now
    if not state.get("terrain_type"):
        missing_fields.append("terrain_type")
    if not state.get("payload_kg"):
        missing_fields.append("payload_kg")

    state["missing_fields"] = missing_fields
    return state