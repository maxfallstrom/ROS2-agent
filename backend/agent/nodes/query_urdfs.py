from agent.helpers.summarize_chat_history import summarize_context_for_embedding
from agent.helpers.vector_search import search_robots
from agent.state import AgentState

async def query_urdfs(state: AgentState) -> dict:
    
    messages = state.get("messages", [])
    
    summary = await summarize_context_for_embedding(messages)

    state["summary_query"] = summary

    try:
        matches = search_robots(summary, threshold=0.3)
    except Exception as e:
        state["error"] = str(e)
        state["matches"] = [
        {"id": "68e827db-4035-4ae0-a43c-158b610e21d5", "name": "ANYmal B", "summary": "The ANYmal B, developed by ANYbotics, is a sophisticated quadrupedal robot designed for versatility and mobility in various environments. With 22 links and 21 joints, it boasts a total mass of approximately 30.4 kg, enabling it to navigate complex terrains efficiently. Its articulated limbs, equipped with multiple revolute joints, allow for dynamic movement and stability, making it ideal for tasks such as inspection in hazardous areas, search and rescue operations, and environmental monitoring. The robot's robust design and advanced locomotion capabilities ensure it can traverse uneven surfaces, making it a valuable asset in both industrial and research applications."},
        {"id": "0f041a8f-88cf-4b9c-93ef-a30e8fe2fdb1", "name": "Go2", "summary": "The Go2, developed by UNITREE Robotics, is a versatile quadruped robot featuring 29 links and 28 joints, allowing for agile movement and stability. Weighing approximately 15 kg, it is designed for various applications, including search and rescue, surveillance, and environmental monitoring. Its advanced joint configurations enable dynamic locomotion across diverse terrains, while integrated sensors like IMU and radar enhance navigation and obstacle detection. The Go2's lightweight structure and robust design make it suitable for both indoor and outdoor tasks, providing a reliable platform for research, exploration, and automation in challenging environments."}
        ]
        state.setdefault("messages", []).append({
            "role": "assistant",
            "content": "Would you like to learn more about one of them? Also, feel free to explore the robots in the view!"
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
