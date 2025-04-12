from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.parse_prompt import parse_prompt
from agent.nodes.query_urdfs import query_urdfs

builder = StateGraph(AgentState)

# Set nodes
builder.add_node("parse_prompt", parse_prompt)
builder.add_node("query_urdfs", query_urdfs)

# Set entry
builder.set_entry_point("parse_prompt")

# Set graph
builder.add_conditional_edges(
    "parse_prompt",
    lambda state: "query" if state.get("status") == "complete" else "ask",
    {
        "ask": END,
        "query": "query_urdfs"
    }
)

builder.add_edge("query_urdfs", END)

# Compile
robot_agent = builder.compile()