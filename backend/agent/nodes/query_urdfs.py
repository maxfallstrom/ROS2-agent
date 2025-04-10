def query_urdfs(state):
    print("[Node] query_urdfs called")
    # Placeholder list of robots, replace later with Supabase
    state["robot_matches"] = [
        {"name": "TurtleBot3", "sdk": "ros2"},
        {"name": "Spot", "sdk": "spot"}
    ]
    return state