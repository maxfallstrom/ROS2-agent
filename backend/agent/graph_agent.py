from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.parse_prompt import parse_prompt
from agent.nodes.check_info import check_info
from agent.nodes.ask_missing_info import ask_missing_info
from agent.nodes.query_urdfs import query_urdfs
from agent.nodes.format_response import format_response

builder = StateGraph(AgentState)

# Set nodes
builder.add_node("parse_prompt", parse_prompt)
builder.add_node("check_info", check_info)
builder.add_node("ask_missing_info", ask_missing_info)
builder.add_node("query_urdfs", query_urdfs)
builder.add_node("format_response", format_response)

# Set entry
builder.set_entry_point("parse_prompt")

# Set graph
builder.add_edge("parse_prompt", "check_info")
builder.add_conditional_edges(
    "check_info",
    lambda state: "ask" if state.get("missing_fields") else "query",
    {
        "ask": "ask_missing_info",
        "query": "query_urdfs"
    }
)
builder.add_edge("ask_missing_info", END)
builder.add_edge("query_urdfs", "format_response")
builder.add_edge("format_response", END)

# Compile
robot_agent = builder.compile()