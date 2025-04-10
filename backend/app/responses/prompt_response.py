from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PromptResponse(BaseModel):
    status: str
    messages: List[Dict[str, Any]]
    robot_matches: Optional[List[Dict[str, Any]]] = None
    missing_fields: Optional[List[str]] = None


def convert_stream_chunk(state: dict) -> dict:
    return {
        "messages": state.get("messages", []),
        "robot_matches": state.get("robot_candidates", []),
        "missing_fields": state.get("required_info", []),
        "code_output": state.get("code_output")
    }
